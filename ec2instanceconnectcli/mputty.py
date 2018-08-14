import argparse
import sys

from ec2instanceconnectcli.EC2InstanceConnectCLI import EC2InstanceConnectCLI
from ec2instanceconnectcli.EC2InstanceConnectCommand import EC2InstanceConnectCommand
from ec2instanceconnectcli.EC2InstanceConnectLogger import EC2InstanceConnectLogger
from ec2instanceconnectcli import input_parser

DEFAULT_USER = ''
DEFAULT_INSTANCE = ''
DEFAULT_PORT = 22
DEFAULT_PROFILE = None

def main(program, mode):
    """
    Parses system arguments sets defaults
    Calls `putty or psftp` to SSH or do file operations using EC2InstanceConnect.

    :param program: Client program to be used for SSH/SFTP operations.
    :type program: basestring
    :param mode: Identifies either SSH/SFTP operation.
    :type mode: basestring
    """

    parser = argparse.ArgumentParser(description="""Usage:
    * mssh-putty [user@]instance_id [-u profile] [-r region] [-z availability_zone] [-i identity_file_ppk] [standard ssh flags] [command]
    * mssh-putty [user@]dns_name -t instance_id [-u profile] [-r region] [-z availability_zone] [-i identity_file_ppk] [standard ssh flags] [command]
    * msftp-putty [user@]instance_id [-u profile] [-r region] [-z availability_zone] [-i identity_file_ppk] [standard sftp flags]
    * msftp-putty [user@]dns_name -t instance_id [-u profile] [-r region] [-z availability_zone] [-i identity_file_ppk] [standard sftp flags]
    """)
    parser.add_argument('-r', '--region', action='store', help='AWS region', type=str)
    parser.add_argument('-z', '--zone', action='store', help='Availability zone', type=str)
    parser.add_argument('-v', '--verbose', help='Enable logging', action="store_true")
    parser.add_argument('-i', '--identity', action='store', help="Required. Identity file in ppk format", type=str)
    parser.add_argument('-u', '--profile', action='store', help='AWS Config Profile', type=str, default=DEFAULT_PROFILE)
    parser.add_argument('-t', '--instance_id', action='store', help='EC2 Instance ID.  Required if target is DNS name or IP address.', type=str, default=DEFAULT_INSTANCE)

    try:
        args = parser.parse_known_args()
    except:
        parser.print_help()
        sys.exit(1)

    #Read public key from ppk file.
    #Public key is unencrypted and in rsa format.
    pub_key_lines = []
    with open(args[0].identity, 'r') as f:
        pub_key_lines = f.readlines()

    #Validate that the identity file format is ppk.
    if pub_key_lines[0].find("PuTTY-User-Key-File-") == -1:
        print("Not a valid Putty key.")
        sys.exit(1)

    #public key starts from 4th line in ppk file.
    line_len = int(pub_key_lines[3].split(':')[1].strip())
    pub_key_lines = pub_key_lines[4:(4+line_len)]
    pub_key = "ssh-rsa "
    for pub_key_line in pub_key_lines:
        pub_key += pub_key_line[:-1]

    logger = EC2InstanceConnectLogger(args[0].verbose)
    instance_bundles, flags, program_command = input_parser.parseargs(args, mode)

    cli_command = EC2InstanceConnectCommand(program, instance_bundles, args[0].identity, flags, program_command, logger.get_logger())
    cli_command.get_command()

    try:
        mssh = EC2InstanceConnectCLI(instance_bundles, pub_key, cli_command, logger.get_logger())
        mssh.invoke_command()
    except Exception as e:
        print("Failed with:\n" + str(e))
        sys.exit(1)
