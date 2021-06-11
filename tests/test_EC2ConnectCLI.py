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

from ec2instanceconnectcli.EC2InstanceConnectCLI import EC2InstanceConnectCLI
from ec2instanceconnectcli.EC2InstanceConnectCommand import EC2InstanceConnectCommand
from ec2instanceconnectcli.EC2InstanceConnectLogger import EC2InstanceConnectLogger
from testloader.test_base import TestBase
try:
    from unittest import mock
except ImportError:
    import mock


class TestEC2InstanceConnectCLI(TestBase):

    @mock.patch('ec2instanceconnectcli.EC2InstanceConnectCLI.EC2InstanceConnectCLI.run_command')
    @mock.patch('ec2instanceconnectcli.key_publisher.push_public_key')
    @mock.patch('ec2instanceconnectcli.ec2_util.get_instance_data')
    def test_mssh_no_target(self,
                  mock_instance_data,
                  mock_push_key,
                  mock_run):
        mock_file = 'identity'
        flag = '-f flag'
        command = 'command arg'
        logger = EC2InstanceConnectLogger()
        instance_bundles = [{'username': self.default_user, 'instance_id': self.instance_id,
                            'target': None, 'zone': self.availability_zone, 'region': self.region,
                            'profile': self.profile}]

        mock_instance_data.return_value = self.instance_info
        mock_push_key.return_value = None

        cli_command = EC2InstanceConnectCommand("ssh", instance_bundles, mock_file, flag, command, logger.get_logger())
        cli = EC2InstanceConnectCLI(instance_bundles, "", cli_command, logger.get_logger())
        cli.invoke_command()
        
        expected_command = 'ssh -o "IdentitiesOnly=yes" -i {0} {1} {2}@{3} \'{4}\''.format(mock_file, flag, self.default_user,
                                                               self.public_ip, command)

        # Check that we successfully get to the run
        self.assertTrue(mock_instance_data.called)
        self.assertTrue(mock_push_key.called)
        # Also check that we get the correct command generated
        mock_run.assert_called_with(expected_command)

    @mock.patch('ec2instanceconnectcli.EC2InstanceConnectCLI.EC2InstanceConnectCLI.run_command')
    @mock.patch('ec2instanceconnectcli.key_publisher.push_public_key')
    @mock.patch('ec2instanceconnectcli.ec2_util.get_instance_data')
    def test_mssh_no_target_no_public_ip(self,
                  mock_instance_data,
                  mock_push_key,
                  mock_run):
        mock_file = "identity"
        flag = '-f flag'
        command = 'command arg'
        logger = EC2InstanceConnectLogger()
        instance_bundles = [{'username': self.default_user, 'instance_id': self.instance_id,
                                     'target': None, 'zone': self.availability_zone, 'region': self.region,
                                     'profile': self.profile}]

        mock_instance_data.return_value = self.private_instance_info
        mock_push_key.return_value = None

        cli_command = EC2InstanceConnectCommand("ssh", instance_bundles, mock_file, flag, command, logger.get_logger())
        cli = EC2InstanceConnectCLI(instance_bundles, "", cli_command, logger.get_logger())
        cli.invoke_command()

        expected_command = 'ssh -o "IdentitiesOnly=yes" -i {0} {1} {2}@{3} \'{4}\''.format(mock_file, flag, self.default_user,
                                                               self.private_ip, command)

        # Check that we successfully get to the run
        self.assertTrue(mock_instance_data.called)
        self.assertTrue(mock_push_key.called)
        mock_run.assert_called_with(expected_command)

    @mock.patch('ec2instanceconnectcli.EC2InstanceConnectCLI.EC2InstanceConnectCLI.run_command')
    @mock.patch('ec2instanceconnectcli.key_publisher.push_public_key')
    @mock.patch('ec2instanceconnectcli.ec2_util.get_instance_data')
    def test_mssh_with_target(self,
                  mock_instance_data,
                  mock_push_key,
                  mock_run):
        mock_file = 'identity'
        flag = '-f flag'
        command = 'command arg'
        host = '0.0.0.0'
        logger = EC2InstanceConnectLogger()
        instance_bundles = [{'username': self.default_user, 'instance_id': self.instance_id,
                                     'target': host, 'zone': self.availability_zone, 'region': self.region,
                                     'profile': self.profile}]

        mock_instance_data.return_value = self.instance_info
        mock_push_key.return_value = None

        cli_command = EC2InstanceConnectCommand("ssh", instance_bundles, mock_file, flag, command, logger.get_logger())
        cli = EC2InstanceConnectCLI(instance_bundles, "", cli_command, logger.get_logger())
        cli.invoke_command()

        expected_command = 'ssh -o "IdentitiesOnly=yes" -i {0} {1} {2}@{3} \'{4}\''.format(mock_file, flag, self.default_user,
                                                               host, command)
        # Check that we successfully get to the run
        # Since both target and availability_zone are provided, mock_instance_data should not be called
        self.assertFalse(mock_instance_data.called)
        self.assertTrue(mock_push_key.called)
        mock_run.assert_called_with(expected_command)

    @mock.patch('ec2instanceconnectcli.EC2InstanceConnectCLI.EC2InstanceConnectCLI.run_command')
    @mock.patch('ec2instanceconnectcli.key_publisher.push_public_key')
    @mock.patch('ec2instanceconnectcli.ec2_util.get_instance_data')
    def test_msftp(self,
                  mock_instance_data,
                  mock_push_key,
                  mock_run):
        mock_file = 'identity'
        flag = '-f flag'
        command = 'file2 file3'
        logger = EC2InstanceConnectLogger()
        instance_bundles = [{'username': self.default_user, 'instance_id': self.instance_id,
                                     'target': None, 'zone': self.availability_zone, 'region': self.region,
                                     'profile': self.profile, 'file': 'file1'}]

        mock_instance_data.return_value = self.instance_info
        mock_push_key.return_value = None

        expected_command = 'sftp -o "IdentitiesOnly=yes" -i {0} {1} {2}@{3}:{4} \'{5}\''.format(mock_file, flag, self.default_user,
                                                               self.public_ip, 'file1', command)

        cli_command = EC2InstanceConnectCommand("sftp", instance_bundles, mock_file, flag, command, logger.get_logger())
        cli = EC2InstanceConnectCLI(instance_bundles, "", cli_command, logger.get_logger())
        cli.invoke_command()

        # Check that we successfully get to the run
        self.assertTrue(mock_instance_data.called)
        self.assertTrue(mock_push_key.called)
        mock_run.assert_called_with(expected_command)

    @mock.patch('ec2instanceconnectcli.EC2InstanceConnectCLI.EC2InstanceConnectCLI.run_command')
    @mock.patch('ec2instanceconnectcli.key_publisher.push_public_key')
    @mock.patch('ec2instanceconnectcli.ec2_util.get_instance_data')
    def test_mscp(self,
                   mock_instance_data,
                   mock_push_key,
                   mock_run):
        mock_file = 'identity'
        flag = '-f flag'
        command = 'file2 file3'
        logger = EC2InstanceConnectLogger()
        instance_bundles = [{'username': self.default_user, 'instance_id': self.instance_id,
                                     'target': None, 'zone': self.availability_zone, 'region': self.region,
                                     'profile': self.profile, 'file': 'file1'},
                                    {'username': self.default_user, 'instance_id': self.instance_id,
                                     'target': None, 'zone': self.availability_zone, 'region': self.region,
                                     'profile': self.profile, 'file': 'file4'}]

        mock_instance_data.return_value = self.instance_info
        mock_push_key.return_value = None

        expected_command = 'scp -o "IdentitiesOnly=yes" -i {0} {1} {2}@{3}:{4} \'{5}\' {6}@{7}:{8}'.format(mock_file, flag, self.default_user,
                                                                                self.public_ip, 'file1', command,
                                                                                self.default_user,
                                                                                self.public_ip, 'file4')

        cli_command = EC2InstanceConnectCommand("scp", instance_bundles, mock_file, flag, command, logger.get_logger())
        cli = EC2InstanceConnectCLI(instance_bundles, "", cli_command, logger.get_logger())
        cli.invoke_command()

        # Check that we successfully get to the run
        self.assertTrue(mock_instance_data.called)
        self.assertTrue(mock_push_key.called)
        mock_run.assert_called_with(expected_command)

    def test_status_code(self):
        #TODO: Refine test for checking run_command status code
        cli = EC2InstanceConnectCLI(None, None, None, None)
        code = cli.run_command("echo ok; exit -1;")
        self.assertEqual(code, 255)
