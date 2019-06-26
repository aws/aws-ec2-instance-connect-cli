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

from unittest import TestCase
import os
from argparse import Namespace


class TestBase(TestCase):
    """
    This class does not actually provide any tests, but serves as common setup for every other test class.
    """

    profile = 'default'
    new_profile = 'newprofile'
    region = 'us-east-2'
    new_region = 'us-west-2'
    user = 'youser'
    default_user = 'ec2-user'
    instance_id = 'i-abcd1234'
    dns_name = 'my.dns.name'
    port = 22
    command = 'uname -a'
    argument = user + '@' + instance_id + ':' + str(port)
    availability_zone = 'us-east-2b'
    public_dns_name = 'ec2-21-0-0-10.us-west-2.compute.amazonaws.com'
    private_dns_name = 'ip-10-0-0-21.us-west-2.compute.internal'
    public_ip = '21.0.0.10'
    private_ip = '10.0.0.21'
    file_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = "{0}/configuration".format(file_dir)
    config_file = "{0}/config".format(config_dir)
    cred_file = "{0}/credentials".format(config_dir)
    access_key = 'notsecret'
    secret_key = 'secret'
    new_access_key = 'notatallsecret'
    new_secret_key = 'supersecret'
    endpoint = 'http://0.0.0.0:6443'
    new_endpoint = 'endpoint.us-east-2.amazon.com'
    home = os.environ.get('HOME')
    if home is None:
        home = os.environ.get('ENVROOT')
    default_config_dir = str(home) + '/.aws'
    default_config_file = os.path.join(default_config_dir, 'config')
    default_creds_file = os.path.join(default_config_dir, 'credentials')
    client_config = {
        'aws_access_key_id': access_key,
        'aws_secret_access_key': secret_key,
        'region_name': region,
        'endpoint_url': endpoint
    }
    instance_info = Namespace(
        public_dns_name=public_dns_name,
        private_dns_name=private_dns_name,
        public_ip=public_ip,
        private_ip=private_ip,
        availability_zone=availability_zone
    )
    private_instance_info = Namespace(
        public_dns_name=None,
        private_dns_name=private_dns_name,
        public_ip=None,
        private_ip=private_ip,
        availability_zone=availability_zone
    )
