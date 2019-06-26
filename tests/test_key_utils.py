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

from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from ec2instanceconnectcli import key_utils
from unittest import mock, TestCase


class TestKeyUtils(TestCase):
    password = 'password'
    mock_key = mock.Mock()
    public_exponent = 65537
    key_size = 2048

    @mock.patch('cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key')
    def test_generate_key(self, mock_gen_key):
        key_utils.generate_key(self.key_size)
        mock_gen_key.assert_called_with(backend=crypto_default_backend(),
                                        public_exponent=self.public_exponent,
                                        key_size=self.key_size)

    def test_invalid_encodings(self):
        try:
            key_utils.serialize_key(self.mock_key, encoding='INVALID')
            self.fail('Invalid encoding accepted')

        except AssertionError:
            pass

        try:
            key_utils.serialize_key(self.mock_key, encoding='OpenSSH', return_private=True)
            self.fail('Private keys shouldn''t accept OpenSSH encoding')

        except AssertionError:
            pass

    def test_public_encodings(self):
        mock_pub_key = mock.Mock()
        self.mock_key.public_key.return_value = mock_pub_key

        calls = [mock.call(encoding=crypto_serialization.Encoding.OpenSSH,
                           format=crypto_serialization.PublicFormat.OpenSSH),
                 mock.call(encoding=crypto_serialization.Encoding.DER,
                           format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo),
                 mock.call(encoding=crypto_serialization.Encoding.PEM,
                           format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)]

        key_utils.serialize_key(self.mock_key, encoding='OpenSSH', return_private=False)
        key_utils.serialize_key(self.mock_key, encoding='DER', return_private=False)
        key_utils.serialize_key(self.mock_key, encoding='PEM', return_private=False)

        mock_pub_key.public_bytes.assert_has_calls(calls)

    @mock.patch('cryptography.hazmat.primitives.serialization.NoEncryption')
    def test_private_encodings(self, mock_encryption):
        mock_enc = mock.Mock()
        mock_encryption.return_value = mock_enc

        calls = [mock.call(encoding=crypto_serialization.Encoding.DER,
                           format=crypto_serialization.PrivateFormat.TraditionalOpenSSL,
                           encryption_algorithm=mock_enc),
                 mock.call(encoding=crypto_serialization.Encoding.PEM,
                           format=crypto_serialization.PrivateFormat.TraditionalOpenSSL,
                           encryption_algorithm=mock_enc)]

        key_utils.serialize_key(self.mock_key, encoding='DER', return_private=True)
        key_utils.serialize_key(self.mock_key, encoding='PEM', return_private=True)

        self.mock_key.private_bytes.assert_has_calls(calls)

    @mock.patch('cryptography.hazmat.primitives.serialization.BestAvailableEncryption')
    def test_private_password(self, mock_encryption):
        mock_enc = mock.Mock()
        mock_encryption.return_value = mock_enc

        key_utils.serialize_key(self.mock_key, encoding='PEM', return_private=True, password=self.password)

        mock_encryption.assert_called_with(self.password)
        self.mock_key.private_bytes.assert_called_with(
            encoding=crypto_serialization.Encoding.PEM,
            format=crypto_serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=mock_enc)

    @mock.patch('ec2instanceconnectcli.key_utils.serialize_key')
    @mock.patch('cryptography.hazmat.primitives.serialization.load_der_private_key')
    def test_convert_der_pem_private(self, mock_load_private, mock_serialize):
        mock_load_private.return_value = self.mock_key

        key_utils.convert_der_to_pem(self.mock_key, is_private=True)

        calls = [mock.call(self.mock_key, encoding='PEM', return_private=True)]

        mock_load_private.assert_called_with(self.mock_key, backend=crypto_default_backend())
        mock_serialize.assert_has_calls(calls)

    @mock.patch('cryptography.hazmat.primitives.serialization.load_der_public_key')
    def test_convert_der_pem_public(self, mock_load_public):
        mock_load_public.return_value = self.mock_key

        key_utils.convert_der_to_pem(self.mock_key, is_private=False)

        mock_load_public.assert_called_with(self.mock_key, backend=crypto_default_backend())
        self.mock_key.public_bytes.assert_called_with(
            encoding=crypto_serialization.Encoding.PEM,
            format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)

    @mock.patch('ec2instanceconnectcli.key_utils.serialize_key')
    @mock.patch('cryptography.hazmat.primitives.serialization.load_pem_private_key')
    def test_convert_pem_der_private(self, mock_load_private, mock_serialize):
        mock_load_private.return_value = self.mock_key

        fake_priv = str.encode("{0}\n".format(key_utils.begin_key.format(key_utils.private_str)))

        key_utils.convert_pem_to_der(fake_priv)

        calls = [mock.call(self.mock_key, encoding='DER', return_private=True)]

        mock_load_private.assert_called_with(fake_priv, backend=crypto_default_backend())
        mock_serialize.assert_has_calls(calls)

    @mock.patch('cryptography.hazmat.primitives.serialization.load_pem_public_key')
    def test_convert_pem_der_public(self, mock_load_public):
        mock_load_public.return_value = self.mock_key

        fake_pub = str.encode("{0}\n".format(key_utils.begin_key.format(key_utils.public_str)))

        key_utils.convert_pem_to_der(fake_pub)

        mock_load_public.assert_called_with(fake_pub, backend=crypto_default_backend())
        self.mock_key.public_bytes.assert_called_with(
                                   encoding=crypto_serialization.Encoding.DER,
                                   format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)

    @mock.patch('cryptography.hazmat.primitives.serialization.load_pem_public_key')
    def test_convert_pem_to_openssh(self, mock_load_public):
        mock_load_public.return_value = self.mock_key

        key_utils.convert_pem_to_openssh(self.mock_key)

        mock_load_public.assert_called_with(self.mock_key, backend=crypto_default_backend())
        self.mock_key.public_bytes.assert_called_with(
            encoding=crypto_serialization.Encoding.OpenSSH,
            format=crypto_serialization.PublicFormat.OpenSSH)
