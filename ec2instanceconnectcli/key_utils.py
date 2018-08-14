from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ssh_rsa_exponent = 65537

private_str = "PRIVATE"
public_str = "PUBLIC"
begin_key = "-----BEGIN RSA {0} KEY-----"
end_key = "-----END RSA {0} KEY-----"
ssh_rsa = "ssh-rsa"


def generate_key(bit_strength):
    """
    Generates an RSA private key.

    :param bit_strength: Bit strength to use for generation
    :type bit_strength: int
    :return: A Python Cryptography RSA key object
    :rtype: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey
    """
    return rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=ssh_rsa_exponent,
        key_size=bit_strength)


def serialize_key(key, encoding='PEM', return_private=False, password=None):
    """
    Given an RSA private key object, return the public or private key in the requested encoding.
    encoded in the requested formats.  Private keys will always use TraditionalOpenSSL format,
    because that's the format supported by Paramiko
    public keys will always use SubjectPublicKeyInfo format UNLESS
    the encoding is 'OpenSSH' (in which case, it will use OpenSSH format).

    :param key: An RSA private key object
    :type key: cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey
    :param encoding: The encoding to use for serializing the private key. Allowed: 'PEM', 'DER', 'OpenSSH'. Default: 'PEM'. \
       Note that if return_private is True then 'OpenSSH' is not allowed.
    :type encoding: basestring
    :param return_private: Whether to return the public or private key.  Default: False.
    :type return_private: bool
    :param password: In bytes, an optional password to use for encoding a private key. Ignored if return_private is False. \
       Default: None
    :type password: basestring
    :return: Encoded key as a byte array
    :rtype: bytearray
    """
    if return_private and encoding == 'OpenSSH':
        raise AssertionError('Private keys cannot be serialized in OpenSSH encoding')

    if encoding == 'OpenSSH':
        assert(not return_private)
        enc = crypto_serialization.Encoding.OpenSSH
    elif encoding == 'PEM':
        enc = crypto_serialization.Encoding.PEM
    elif encoding == 'DER':
        enc = crypto_serialization.Encoding.DER
    else:
        raise AssertionError('Unrecognized encoding {0}'.format(encoding))

    if return_private:
        if password:
            enc_alg = crypto_serialization.BestAvailableEncryption(password)
        else:
            enc_alg = crypto_serialization.NoEncryption()

        return key.private_bytes(
            encoding=enc,
            format=crypto_serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=enc_alg
        )

    else:
        if encoding == 'OpenSSH':
            format = crypto_serialization.PublicFormat.OpenSSH
        else:
            format = crypto_serialization.PublicFormat.SubjectPublicKeyInfo

        return key.public_key().public_bytes(
            encoding=enc,
            format=format
        )


def convert_der_to_pem(der_key, is_private=False):
    """
    Converts a given key from DER to PEM format.

    :param der_key: DER-encoded key bytes
    :type der_key: bytearray
    :param is_private: Whether the key is public or private. Default: False
    :type is_private: bool
    :return: PEM-encoded key bytes
    :rtype: bytearray
    """
    if is_private:
        loaded_key = crypto_serialization.load_der_private_key(der_key, backend=crypto_default_backend())
        return serialize_key(loaded_key, encoding='PEM', return_private=is_private)
    else:
        loaded_key = crypto_serialization.load_der_public_key(der_key, backend=crypto_default_backend())
        return loaded_key.public_bytes(encoding=crypto_serialization.Encoding.PEM,
                                       format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)


def convert_pem_to_der(pem_key):
    """
    Converts a given key from PEM to DER format.

    :param pem_key: PEM-encoded key bytes
    :type pem_key: bytearray
    :return: DER-encoded key bytes
    :rtype: bytearray
    """
    first_line = pem_key.decode().split('\n', 1)[0]
    is_private = first_line == begin_key.format(private_str)
    if is_private:
        loaded_key = crypto_serialization.load_pem_private_key(pem_key, backend=crypto_default_backend())
        return serialize_key(loaded_key, encoding='DER', return_private=is_private)
    else:
        loaded_key = crypto_serialization.load_pem_public_key(pem_key, backend=crypto_default_backend())
        return loaded_key.public_bytes(encoding=crypto_serialization.Encoding.DER,
                                       format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)


def convert_pem_to_openssh(pem_key):
    """
    Converts a given public key from PEM to OpenSSH format.

    :param pem_key: PEM-encoded key bytes
    :type pem_key: bytearray
    :return: OpenSSH-encoded key bytes
    :rtype: bytearray
    """
    loaded_key = crypto_serialization.load_pem_public_key(pem_key, backend=crypto_default_backend())
    return loaded_key.public_bytes(encoding=crypto_serialization.Encoding.OpenSSH,
                                   format=crypto_serialization.PublicFormat.OpenSSH)
