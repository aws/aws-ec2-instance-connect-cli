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

import argparse
import getpass
from ec2instanceconnectcli import input_parser
from testloader.test_base import TestBase


class TestInputParser(TestBase):

    parser = argparse.ArgumentParser(description='alternate usage: mssh [user]@[instance-id]:[port]')
    parser.add_argument('-u', '--profile', help='AWS Config Profile', type=str, default='default')
    parser.add_argument('-t', '--instance_id', help='EC2 Instance ID', type=str, default='')
    parser.add_argument('-r', '--region', action='store', help='AWS region', type=str)
    parser.add_argument('-z', '--zone', action='store', help='Availability zone', type=str)
    parser.add_argument('-U', '--dest_profile', action='store',
                        help='AWS Config Profile (if specifying second instance as destination)', type=str, default='default')
    parser.add_argument('-R', '--dest_region', action='store',
                        help='AWS region (if specifying second instance as destination)', type=str)
    parser.add_argument('-Z', '--dest_zone', action='store',
                        help='Availability zone (if specifying second instance as destination', type=str)
    parser.add_argument('-T', '--dest_instance_id', action='store', type=str, default='',
                        help='EC2 Instance ID. Required if destination is a second instance and is given as a DNS name'
                             'or IP address')
    parser.add_argument('-ssm', '--ssm_connect', action='store_true', help='Connect to instance with instance id through SSM')

    def test_basic_target(self):
        args = self.parser.parse_known_args(['-u', self.profile, self.instance_id])

        bundles, flags, command = input_parser.parseargs(args)

        self.assertEqual(bundles, [{'username': self.default_user, 'instance_id': self.instance_id,
                                   'target': None, 'zone': None, 'region': None, 'ssm': False, 'profile': self.profile}])
        self.assertEqual(flags, '')
        self.assertEqual(command, '')

    def test_ssm_target(self):
        args = self.parser.parse_known_args(['-u', self.profile, '-ssm', self.instance_id])

        bundles, flags, command = input_parser.parseargs(args)

        self.assertEqual(bundles, [{'username': self.default_user, 'instance_id': self.instance_id,
                                   'target': None, 'zone': None, 'region': None, 'ssm': True, 'profile': self.profile}])
        self.assertEqual(flags, '')
        self.assertEqual(command, '')

    def test_username(self):
        args = self.parser.parse_known_args(['-u', self.profile, "myuser@{0}".format(self.instance_id)])

        bundles, flags, command = input_parser.parseargs(args)

        self.assertEqual(bundles, [{'username': 'myuser', 'instance_id': self.instance_id,
                                    'target': None, 'zone': None, 'region': None, 'ssm': False, 'profile': self.profile}])
        self.assertEqual(flags, '')
        self.assertEqual(command, '')

    def test_dns_name(self):
        args = self.parser.parse_known_args(['-u', self.profile, '-t', self.instance_id, '-r', self.region,
                                             '-z', self.availability_zone, self.dns_name])

        bundles, flags, command = input_parser.parseargs(args)

        self.assertEqual(bundles, [{'username': self.default_user, 'instance_id': self.instance_id,
                                    'target': self.dns_name, 'zone': self.availability_zone,
                                    'region': self.region, 'ssm': False, 'profile': self.profile}])
        self.assertEqual(flags, '')
        self.assertEqual(command, '')

    def test_flags(self):
        args = self.parser.parse_known_args(['-u', self.profile, "-1", "-l", "login", self.instance_id])

        bundles, flags, command = input_parser.parseargs(args)

        self.assertEqual(bundles, [{'username': 'login', 'instance_id': self.instance_id,
                                    'target': None, 'zone': None, 'region': None, 'ssm': False, 'profile': self.profile}])
        self.assertEqual(flags, '-1 -l login')
        self.assertEqual(command, '')

    def test_command(self):
        args = self.parser.parse_known_args(['-u', self.profile, self.instance_id, 'uname', '-a'])

        bundles, flags, command = input_parser.parseargs(args)

        self.assertEqual(bundles, [{'username': self.default_user, 'instance_id': self.instance_id,
                                    'target': None, 'zone': None, 'region': None, 'ssm': False, 'profile': self.profile}])
        self.assertEqual(flags, '')
        self.assertEqual(command, 'uname -a')

    def test_sftp(self):
        args = self.parser.parse_known_args(['-u', self.profile, "{0}:{1}".format(self.instance_id, 'first_file'),
                                             'second_file'])

        bundles, flags, command = input_parser.parseargs(args, 'sftp')

        self.assertEqual(bundles, [{'username': self.default_user, 'instance_id': self.instance_id,
                                    'target': None, 'zone': None, 'region': None, 'ssm': False, 'profile': self.profile,
                                    'file': 'first_file'}])
        self.assertEqual(flags, '')
        self.assertEqual(command, 'second_file')

    def test_invalid_username(self):
        args = self.parser.parse_known_args(['-u', self.profile, "BADUSER@{0}".format(self.instance_id)])

        self.assertRaises(AssertionError, input_parser.parseargs, args)

    def test_invalid_ip(self):
        args = self.parser.parse_known_args(['-u', self.profile, '-t', self.instance_id, '-r', self.region,
                                             '-z', self.availability_zone, '123.123.123.555'])

        self.assertRaises(AssertionError, input_parser.parseargs, args)

    def test_invalid_dns_name(self):
        args = self.parser.parse_known_args(['-u', self.profile, '-t', self.instance_id, '-r', self.region,
                                             '-z', self.availability_zone, 'I!nv&ali$d'])

        self.assertRaises(AssertionError, input_parser.parseargs, args)

    def test_double_at(self):
        args = self.parser.parse_known_args(['-u', self.profile, '-t', self.instance_id, '-r', self.region,
                                             '-z', self.availability_zone, 'I!nv&@li@d'])

        self.assertRaises(AssertionError, input_parser.parseargs, args)

    def test_invalid_region(self):
        args = self.parser.parse_known_args(['-u', self.profile, '-t', self.instance_id, '-r', 'bad region',
                                             '-z', self.availability_zone, self.dns_name])

        self.assertRaises(AssertionError, input_parser.parseargs, args)

    def test_invalid_zone(self):
        args = self.parser.parse_known_args(['-u', self.profile, '-t', self.instance_id, '-r', self.region,
                                             '-z', 'bad zone', self.dns_name])

        self.assertRaises(AssertionError, input_parser.parseargs, args)
