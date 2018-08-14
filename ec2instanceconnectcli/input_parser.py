import re
import socket

INSTANCE_ID_RE = re.compile("i-[a-f0-9]+")
UNIX_USER_RE = re.compile("[a-z_][a-z0-9_-]*[$]?")  # Taken from useradd manpage
REGION_RE = re.compile("([a-z]+-)+[0-9]+")
ZONE_RE = re.compile("([a-z]+-)+[0-9]+[a-z]")

def parseargs(args, mode='ssh'):
    """
    Parses the input arguments to one of the EC2 Instance Connect CLI commands and splits it into pieces that will be
    used as appropriate at invocation time.

    All commands (ssh, sftp,) follow the same basic structure of
    protocol [ec2 connect flags] [command flags] [target] [command or files]

    The first two are free - protocol is the mode, ec2 connect flags we get from argparse in args[0]
    The rest we need to extract from args[1]
    What makes this particularly interesting is that the data we need varies by command.
    - For ssh, we need the user (if present), host (required), and command (if present)
    - For sftp, we need the user (if present), host (required), and dir or files (if present)

    To match this, we have a structure that may contain a given target's instance ID, target DNS/IP/etc,
    username to use for connection, EC2 availability zone, and/or a file associated with that host in the given command.
    There will be either one or two depending on what mode we're parsing for.

    The command field is then used to store either the ssh command or additional files passed to sftp.

    :param args: A tuple of known arguments and list of string with unknown arguments
    :type args: tuple
    :param mode: The protocol we will be using (ssh, sftp, potentially others in-future)
    :type mode: basestring
    :return: Args split into three pieces: EC2 instance information, command flags, and and the actual command to run
    :rtype: tuple
    """

    if len(args) < 2:
        raise AssertionError('No target was provided')
    if len(args[1]) < 1:
        raise AssertionError('No target was provided')

    """
    Our flags.  As these are via argparse they're free.
    Instance details are a bit weird.  Since the instance ID can either be the actual "host" or a flag we have to group it.
    We do this with an "instance bundle" dict.
    Note we don't load the actual instance DNS/IP/ID here - that comes later.
    """
    instance_bundles = [
        {
            'profile': args[0].profile,
            'instance_id': args[0].instance_id,
            'region': args[0].region,
            'zone': args[0].zone
        }
    ]
    # We do this as an array to support future commands that may need multiple instances (eg, scp)

    # Process out the command flags & target data
    flags, command, instance_bundles = _parse_command_flags(args[1], instance_bundles, is_ssh=(mode=='ssh'))

    # Process the instance & target data to give us an actual picture of what end hosts we're working with
    instance_bundles = _parse_instance_bundles(instance_bundles)

    return instance_bundles, flags, command


def _parse_command_flags(raw_command, instance_bundles, is_ssh=False):
    """
    Parses the command from the user and strips out two pieces:
    1) The flags for the underlying command
    2) The actual underlying command or file list for ssh/sftp/etc

    :param raw_command: The raw command string, ie, anything not recognized by argparse
    :type raw_command: basestring
    :param instance_bundles: dicts containing information about desired EC2 instances
    :type instance_bundles: list
    :param is_ssh: Specifies if we are running an ssh command.  There is an extra flag we consider if so.
    :type is_ssh: bool
    :return: tuple of flags and final comamnd or file list
    :rtype: tuple
    """
    # TODO: We do not currently handle the user passing the '-i' flag.
    flags = ''
    is_user = False
    is_flagged = False
    command_index = 0
    used = 0
    """
    Flags for the underlying command.  These will always be in the format -[flag indicator] [flag value]
    """
    while command_index < len(raw_command) - 1:
        if raw_command[command_index][0] != '-' and not is_flagged:
            # We found something that's not a flag or a flag value.  Exit flag loop.
            break

        used += 1

        # This is either a flag or a flag value
        flags = '{0} {1}'.format(flags, raw_command[command_index])

        if raw_command[command_index][0] == '-':
            # Flag
            is_flagged = True
            if raw_command[command_index][1] == 'l' and is_ssh:
                # We want to extract the user flag for ssh mode
                is_user = True

        else:
            # Flag value
            is_flagged = False
            if is_user:
                # We want to extract the user flag for ssh mode
                instance_bundles[0]['username'] = raw_command[command_index]
                is_user = False

        command_index += 1

    flags = flags.strip()

    """
    Target host and command or file list
    """

    if used == len(raw_command) and len(raw_command) != 1:
        # EVERYTHING was a flag or flag value
        raise AssertionError('No target was provided')

    # Target
    instance_bundles[0]['target'] = raw_command[command_index]
    command_index += 1

    # Command/file list
    command_end = len(raw_command)
    command = ' '.join(raw_command[command_index:command_end])

    return flags, command, instance_bundles


def _parse_instance_bundles(instance_bundles):
    """
    Processes instance bundles.  The goal is to establish the final data on instance IDs
    and FQDNs/IPs and any target file to include for sftp
    This includes data validity checks.

    :param instance_bundles: The unprocessed instance bundle objects
    :type instance_bundles: list
    :return: Processed instance bundle objects
    :rtype: list
    """
    for bundle in instance_bundles:
        # We parse target in a specific order based on mode due to how commands prioritize/mark parts optional
        if '@' in bundle['target']:
            if len(bundle['target'].split('@')) > 2:
                # Host details includes an @.  Invalid.
                raise AssertionError('Target DNS or IP address is invalid')
            # A user was specified
            bundle['username'], bundle['target'] = bundle['target'].split('@')
        if ':' in bundle['target']:
            # May be present for sftp
            bundle['target'], bundle['file'] = bundle['target'].split(':')

        if bundle.get('target', None):
            if INSTANCE_ID_RE.match(bundle['target'].lower()):
                # We might have an instance as the target AND an instance flag and they don't match
                # Since ssh prioritizes user@ over -l login_name, we will prioritize the target over the flag
                # If we don't have the flag, we use the target anyways
                bundle['instance_id'] = bundle['target']
                bundle['target'] = None

        if len(bundle.get('username', '')) == 0:
            bundle['username'] = 'ec2-user'

        # Validate region & zone if present
        if bundle.get('region') and len(bundle.get('region')) > 0:
            if REGION_RE.match(bundle['region']) is None:
                raise AssertionError('{0} is not a valid region'.format(bundle['region']))

        if bundle.get('zone') and len(bundle.get('zone')) > 0:
            if ZONE_RE.match(bundle['zone']) is None:
                raise AssertionError('{0} is not a valid zone'.format(bundle['zone']))

        # Validate username
        if not _is_valid_username(bundle['username']):
            raise AssertionError('{0} is not a valid UNIX username'.format(bundle['username']))

        # Validate instance ID format
        if len(bundle['instance_id']) > 0 and not INSTANCE_ID_RE.match(bundle['instance_id'].lower()):
            raise AssertionError('Instance ID {0} is not valid'.format(bundle['instance_id']))

        # Validate DNS/IP/hostname/etc
        if bundle.get('target', None):
            if not _is_valid_target(bundle.get('target', '')):
                # It might be an IP
                raise AssertionError('Target DNS or IP address is invalid')

    return instance_bundles


def _is_valid_username(username):
    """
    Validates if the provided username is a valid UNIX username

    :param username: username to validate
    :type username: basestring
    :return: Whether the given username is a valid UNIX username
    :rtype: bool
    """
    return UNIX_USER_RE.match(username) is not None


def _is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError: # inet_pton is not available
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False

    return True


def _is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:
        return False
    return True


def _is_valid_target(hostname):
    """
    Validates if the provided "hostname" is a valid DNS name or IP address

    :param hostname: FQDN to validate
    :type hostname: basestring
    :return: Whether the given hostname is a valid DNS name or IP address
    :rtype: bool
    """
    if not hostname:
        return False

    # Check if it's a valid IP
    if _is_valid_ipv4_address(hostname) or _is_valid_ipv6_address(hostname):
        return True

    # Check if it's a valid DNS name

    if hostname[-1] == '.':
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    if len(hostname) < 1 or len(hostname) > 253: # Technically 255 octets but 2 are used for encoding
        return False

    labels = hostname.split(".")

    # the TLD must be not all-numeric
    if re.match(r"[0-9]+$", labels[-1]):
        return False

    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(label) for label in labels)
