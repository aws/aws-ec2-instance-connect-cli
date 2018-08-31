import logging
import sys
import time
from subprocess import Popen

import botocore.session
from ec2instanceconnectcli import __version__ as CLI_VERSION
from ec2instanceconnectcli import ec2_util, key_publisher


class EC2InstanceConnectCLI(object):
    """
    SSH Transport via socket to EC2 Instance
    Pushes public key to EC2 Instance Metadata Service (via AWS EC2 Instance Connect) and
    establishes an SSH connection using the respective private key
    """

    def __init__(self, instance_bundles, pub_key, cli_command, logger):
        """
        :param instance_bundles: list of dicts that provide dns name, zone, etc information about EC2 instances
        :type instance_bundles: list
        :param pub_key: ssh public key
        :type pub_key: basestring
        :param cli_command: command to run in underlying shell
        :type cli_command: basestring
        :param logger: CLI logging utility to send log messages to
        :type logger: ec2instanceconnectcli.EC2InstanceConnectLogger.EC2InstanceConnectLogger
        """
        self.instance_bundles = instance_bundles
        self.pub_key = pub_key
        self.logger = logger
        self.cli_command = cli_command

    def call_ec2(self):
        """
        Fetches information on the associated EC2 instance
        """

        for bundle in self.instance_bundles:
            session = bundle['session']
            #If bundle['target'] has a value, then use it.
            if bundle['target']:
                bundle['host_info'] = bundle['target']
            else:
                bundle['host_info'] = None

            if (bundle['target'] and bundle['zone']) or len(bundle['instance_id']) == 0:
                # If both are specified or we're not using an instance then we have no reason to call EC2
                self.logger.debug("{0} does not require lookup".format(bundle['target']))
                continue

            instance_info = ec2_util.get_instance_data(session, bundle['instance_id'])
            bundle['zone'] = instance_info.availability_zone
            #If host_info is not available, fallback to using public ipaddress and then private ipaddress.
            if not bundle['host_info']:
                bundle['host_info'] = instance_info.public_ip if instance_info.public_ip else instance_info.private_ip
            self.logger.debug('Successfully got instance information from EC2 API for {0}'.format(bundle['instance_id']))

    def handle_keys(self):
        """
        Pushes the public key to the EC2 Instance(s) using AWS EC2 Instance Connect
        """
        for bundle in self.instance_bundles:
            session = bundle['session']
            if len(bundle['instance_id']) == 0:
                self.logger.debug("{0} does not require pushing public key using EC2InstanceConnect".format(bundle['target']))
                continue
            key_publisher.push_public_key(session, bundle['instance_id'], bundle['username'], self.pub_key, bundle['zone'])
            self.logger.debug('Successfully pushed the public key to {0}'.format(bundle['instance_id']))

    def run_command(self, command=None):
        """
        Runs the given command in a sub-shell
        :param command: Command to invoke
        :type command: basestring
        """
        if not command:
            raise ValueError('Must provide a command')

        invocation_proc = Popen(command, shell=True)
        while invocation_proc.poll() is None: #sub-process not terminated
            time.sleep(0.1)

    def invoke_command(self):
        """
        Generates the appropriate shell command and invokes it
        """
        try:
            for bundle in self.instance_bundles:
                session = self._get_botocore_session(profile_name=bundle['profile'], region=bundle['region'])
                # enable debug logging on botocore session if command line debug option is set
                if self.logger.getEffectiveLevel() == logging.DEBUG:
                    session.set_debug_logger()
                bundle['session'] = session

            self.call_ec2()
            self.handle_keys()

            #important to generate the command after calling call_ec2 and handle_keys
            self.run_command(self.cli_command.get_command())

        except Exception as e:
            self.logger.error("Failed with: " + str(e))
            sys.exit(1)

    @staticmethod
    def _get_botocore_session(profile_name=None, region=None):
        """
        Generates a botocore session with Managed SSH CLI set as the user agent

        :param profile_name: The name of a profile to use.  If not given, then the \
            default profile is used.
        :type profile_name: string
        :param region: An AWS region name to set as the default for the Botocore session
        :type region: string
        :return: A Botocore session object
        :rtype: botocore.session.Session
        """
        session = botocore.session.get_session()
        botocore_info = 'Botocore/{0}'.format(session.user_agent_version)
        if session.user_agent_extra:
            session.user_agent_extra += ' ' + botocore_info
        else:
            session.user_agent_extra = botocore_info
        session.user_agent_name = 'aws-ec2-instance-connect-cli'
        session.user_agent_version = CLI_VERSION

        """
        # Credential precedence:
        # 1. set user passed profile.
        # 2. set user passed region.
        # 3. let botocore handle the rest.
        """

        if profile_name:
            session.set_config_variable('profile', profile_name)
        if region is not None:
            session.set_config_variable('region', region)

        return session
