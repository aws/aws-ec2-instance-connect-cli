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

from testloader.test_base import TestBase
from ec2instanceconnectcli import ec2_util
try:
    from unittest import mock
except ImportError:
    import mock


class TestEC2Util(TestBase):

    def test_get_instance_data(self):

        describe_instance_correct_return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': self.instance_id,
                            'Placement': {
                                'AvailabilityZone': self.availability_zone,
                            },
                            'PublicDnsName': self.public_dns_name,
                            'PrivateDnsName': self.private_dns_name,
                            'PublicIpAddress': self.public_ip,
                            'PrivateIpAddress': self.private_ip
                        },
                    ],
                },
            ],
        }

        mock_session = mock.Mock()
        mock_boto_client = mock.Mock()
        mock_session.create_client.return_value = mock_boto_client
        mock_boto_client.describe_instances.return_value = describe_instance_correct_return_value

        instance_info = ec2_util.get_instance_data(mock_session, self.instance_id)
        mock_boto_client.describe_instances.assert_called_with(InstanceIds=[self.instance_id])

        self.assertEqual(instance_info.public_dns_name, self.public_dns_name)
        self.assertEqual(instance_info.private_dns_name, self.private_dns_name)
        self.assertEqual(instance_info.public_ip, self.public_ip)
        self.assertEqual(instance_info.private_ip, self.private_ip)
        self.assertEqual(instance_info.availability_zone, self.availability_zone)

    def test_invalid_key_in_response(self):

        describe_instance_wrong_return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': self.instance_id,
                            'WRONG': {
                            },
                        },
                    ],
                },
            ],
        }

        mock_session = mock.Mock()
        mock_boto_client = mock.Mock()
        mock_session.create_client.return_value = mock_boto_client
        mock_boto_client.describe_instances.return_value = describe_instance_wrong_return_value

        with self.assertRaises(SystemExit) as context:
            ec2_util.get_instance_data(mock_session, self.instance_id)
        self.assertEqual(context.exception.code, 1)

    def test_blank_return_values(self):

        describe_instance_blank_return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': self.instance_id,
                            'Placement': {
                                'AvailabilityZone': '',
                            },
                        },
                    ],
                },
            ],
        }

        mock_session = mock.Mock()
        mock_boto_client = mock.Mock()
        mock_session.create_client.return_value = mock_boto_client
        mock_boto_client.describe_instances.return_value = describe_instance_blank_return_value

        with self.assertRaises(SystemExit) as context:
            ec2_util.get_instance_data(mock_session, self.instance_id)
            mock_boto_client.describe_instances.assert_called_with(InstanceIds=[self.instance_id])
        self.assertEqual(context.exception.code, 7)

    def test_no_dns_or_ip(self):

        describe_instance_blank_return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': self.instance_id,
                            'Placement': {
                                'AvailabilityZone': self.availability_zone,
                            },
                            'PublicDnsName': None,
                            'PrivateDnsName': None,
                            'PublicIpAddress': None,
                            'PrivateIpAddress': None
                        },
                    ],
                },
            ],
        }

        mock_session = mock.Mock()
        mock_boto_client = mock.Mock()
        mock_session.create_client.return_value = mock_boto_client
        mock_boto_client.describe_instances.return_value = describe_instance_blank_return_value

        with self.assertRaises(SystemExit) as context:
            ec2_util.get_instance_data(mock_session, self.instance_id)
            mock_boto_client.describe_instances.assert_called_with(InstanceIds=[self.instance_id])
        self.assertEqual(context.exception.code, 8)
