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

from ec2instanceconnectcli import key_publisher
from testloader.test_base import TestBase
from unittest import mock


class TestKeyPublisher(TestBase):

    def test_push_public_key(self):
        mock_session = mock.Mock()
        mock_boto_client = mock.Mock()
        mock_session.create_client.return_value = mock_boto_client

        params = {
                  'InstanceId': self.instance_id,
                  'InstanceOSUser': self.default_user,
                  'SSHPublicKey': 'pub_key',
                  'AvailabilityZone': self.availability_zone
        }

        key_publisher.push_public_key(mock_session, self.instance_id,
                                      self.default_user, 'pub_key', self.availability_zone)

        mock_boto_client.send_ssh_public_key.assert_called_with(**params)
