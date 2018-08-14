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
