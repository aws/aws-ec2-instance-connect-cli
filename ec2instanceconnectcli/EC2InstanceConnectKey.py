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

import os
import tempfile

from ec2instanceconnectcli import key_utils


class EC2InstanceConnectKey(object):
    """
    Generates 2048 bit RSA SSH key pair to be used in conjunction with the CLI.
    Writes the private key to a temporary file on disk and changes it's permissions to 600 (read/write only by owner)
    """
    def __init__(self, logger):
        """
        :param logger: EC2 Instance Connect CLI logger to use for log messages
        :type logger: ec2instanceconnectcli.EC2InstanceConnectLogger.EC2InstanceConnectLogger
        """
        self.logger = logger
        key = key_utils.generate_key(2048)
        self.pub_key = key_utils.serialize_key(key, encoding='OpenSSH').decode('utf-8')
        priv_key = key_utils.serialize_key(key, return_private=True).decode('utf-8')
        self.tempf = self._write_priv_key(priv_key)

    def _write_priv_key(self, _priv_key):
        """
        Writes the private key to the pre-determined temp file

        :param _priv_key: private key body
        :type _priv_key: bytearray
        """
        tempf = tempfile.NamedTemporaryFile(delete=False)
        with open(tempf.name, 'w') as f:
            f.write(_priv_key)
            os.chmod(tempf.name, 0o600)
        tempf.file.close()
        return tempf

    def get_pub_key(self):
        """
        Returns the generated RSA public key.

        :return: Public key body
        :rtype: bytearray
        """
        return self.pub_key

    def get_priv_key_file(self):
        """
        Returns either user provided key file or the temp file with generated RSA private key.

        :return: Private key filepath
        :rtype: basestring
        """
        return self.tempf.name

    def __del__(self):
        """
        Remove the temp file with private key.
        """
        if self.tempf is not None:
            self.logger.debug('Deleting the private key file: {0}'.format(self.tempf.name))
            os.remove(self.tempf.name)
