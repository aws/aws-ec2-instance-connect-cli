# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import sys
import argparse

from ec2instanceconnectcli.EC2InstanceConnectCLI import EC2InstanceConnectCLI
from ec2instanceconnectcli.EC2InstanceConnectKey import EC2InstanceConnectKey
from ec2instanceconnectcli.EC2InstanceConnectCommand import EC2InstanceConnectCommand
from ec2instanceconnectcli.EC2InstanceConnectLogger import EC2InstanceConnectLogger
from ec2instanceconnectcli import input_parser

DEFAULT_INSTANCE = ''
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

    usage = ""
    if mode == "ssh":
        usage="""
            mssh [-t instance_id] [-u profile] [-z availability_zone] [-r region] [supported ssh flags] target [command]

            target                => [user@]instance_id | [user@]hostname
            [supported ssh flags] => [-l login_name] [-p port]
        """
    elif mode == "sftp":
        usage="""
            msftp [-u aws_profile] [-z availability_zone] [supported sftp flags] target
            target                 => [user@]instance_id[:file ...][:dir[/]] | [user@]hostname[:file ...][:dir[/]]
            [supported sftp flags] => [-P port] [-b batchfile]
        """

    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('-r', '--region', action='store', help='AWS region', type=str, metavar='')
    parser.add_argument('-z', '--zone', action='store', help='Availability zone', type=str, metavar='')
    parser.add_argument('-u', '--profile', action='store', help='AWS Config Profile', type=str, default=DEFAULT_PROFILE, metavar='')
    parser.add_argument('-t', '--instance_id', action='store', help='EC2 Instance ID. Required if target is hostname', type=str, default=DEFAULT_INSTANCE, metavar='')
    parser.add_argument('-ssm', '--ssm_connect', action='store_true', help='Connect to instance with instance id through SSM')
    parser.add_argument('-d', '--debug', action="store_true", help='Turn on debug logging')

    args = parser.parse_known_args()

    logger = EC2InstanceConnectLogger(args[0].debug)
    try:
        instance_bundles, flags, program_command = input_parser.parseargs(args, mode)
    except Exception as e:
        print(str(e))
        parser.print_help()
        sys.exit(1)

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
