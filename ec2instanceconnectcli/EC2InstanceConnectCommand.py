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

class EC2InstanceConnectCommand(object):
    """
    Generates commands relevant for the client.
    """

    def __init__(self, program, instance_bundles, key_file, flags, program_command, logger):
        """
        Utility class to generate program specific command.

        :param program: Client program to be invoked by the CLI.
        :type program: basestring
        :param key_file: private key file name.
        :type key_file: basestring
        :param flags: program specific flags.
        :type flags: basestring
        :param program_command: program specific ad-hoc command.
        :type program_command: basestring
        :param logger: EC2 Instance Connect CLI logger to write log messages to
        :type logger: ec2instanceconnectcli.EC2InstanceConnectLogger.EC2InstanceConnectLogger
        """
        self.logger = logger
        self.program = program
        self.instance_bundles = instance_bundles
        self.key_file = key_file
        self.flags = flags
        self.program_command = program_command

    def get_command(self):
        """
        Generates and returns the generated command
        """
        # Start with protocol & identity file
        command = "{0} -i {1}".format(self.program, self.key_file)

        # Next add command flags if present
        if len(self.flags) > 0:
            command = "{0} {1}".format(command, self.flags)

        # Target
        command = "{0} {1}".format(command, self._get_target(self.instance_bundles[0]))

        #program specific command
        if len(self.program_command) > 0:
            command = "{0} {1}".format(command, self.program_command)

        if len(self.instance_bundles) > 1 and self.program == 'ssh':
            command = "{0} -o \"ProxyCommand=ssh -i {1} -W '[%h]:%p' {2}\"".format(command, self.key_file, self._get_target(self.instance_bundles[1]))
        elif len(self.instance_bundles) > 1:
            command = "{0} {1}".format(command, self._get_target(self.instance_bundles[1]))

        self.logger.debug('Generated command: {0}'.format(command))

        return command

    @staticmethod
    def _get_target(instance_bundle):
        """
        Determines the ssh target (and potentially sftp file target) for a given EC2 instance bundle dict
        :param instance_bundle: dict of information on the desired EC2 instance
        :type instance_bundle: dict
        :return: target in the form "user@host[:file]"
        :rtype: basestring
        """
        target = ''
        if instance_bundle.get('host_info', None):
            target = "{0}@{1}".format(instance_bundle['username'], instance_bundle['host_info'])
        # file will exist only for SFTP and SCP operations.
        if instance_bundle.get('file', None):
            target = "{0}:{1}".format(target, instance_bundle['file']).lstrip(':')

        return target
