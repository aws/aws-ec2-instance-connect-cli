import sys
import argparse

from ec2instanceconnectcli.EC2InstanceConnectCLI import EC2InstanceConnectCLI
from ec2instanceconnectcli.EC2InstanceConnectKey import EC2InstanceConnectKey
from ec2instanceconnectcli.EC2InstanceConnectCommand import EC2InstanceConnectCommand
from ec2instanceconnectcli.EC2InstanceConnectLogger import EC2InstanceConnectLogger
from ec2instanceconnectcli import input_parser


DEFAULT_USER = ''
DEFAULT_INSTANCE = ''
DEFAULT_PORT = 22
DEFAULT_PROFILE = None


def main(program, mode):
    """
    Parses system arguments and sets defaults
    Calls `ssh` or `sftp` to SSH into the Instance or transfer files.

    :param program: Client program to be used for SSH/SFTP operations.
    :type program: basestring
    :param mode: Identifies either SSH/SFTP operation.
    :type mode: basestring
    """

    parser = argparse.ArgumentParser(description="""Usage:
    * mssh [user@]instance_id [-u profile] [-z availability_zone] [standard ssh flags] [command]
    * mssh [user@]dns_name -t instance_id [-u profile] [-z availability_zone] [standard ssh flags] [command]
    * msftp [user@]instance_id [-u aws_profile] [-z availability_zone] [standard sftp flags]
    * msftp [user@]dns_name -t instance_id [-u aws_profile] [-z availability_zone] [standard sftp flags]
    As standard for SFTP, the target may be followed by [:file ...] or [:dir[/]]
    """)
    parser.add_argument('-r', '--region', action='store', help='AWS region', type=str)
    parser.add_argument('-z', '--zone', action='store', help='Availability zone', type=str)
    parser.add_argument('-v', '--verbose', help='Enable logging', action="store_true")

    parser.add_argument('-u', '--profile', action='store', help='AWS Config Profile', type=str, default=DEFAULT_PROFILE)
    parser.add_argument('-t', '--instance_id', action='store', help='EC2 Instance ID.  Required if target is DNS name or IP address.', type=str, default=DEFAULT_INSTANCE)

    try:
        args = parser.parse_known_args()
    except:
        parser.print_help()
        sys.exit(1)

    logger = EC2InstanceConnectLogger(args[0].verbose)
    instance_bundles, flags, program_command = input_parser.parseargs(args, mode)

    #Generate temp key
    cli_key = EC2InstanceConnectKey(logger.get_logger())
    cli_command = EC2InstanceConnectCommand(program, instance_bundles, cli_key.get_priv_key_file(), flags, program_command, logger.get_logger())

    try:
        # TODO: Handling for if the '-i' flag is passed
        cli = EC2InstanceConnectCLI(instance_bundles, cli_key.get_pub_key(), cli_command, logger.get_logger())
        cli.invoke_command()
    except Exception as e:
        print('Failed with:\n' + str(e))
        sys.exit(1)
