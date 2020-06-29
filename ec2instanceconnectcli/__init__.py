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
"""
EC2InstanceConnectCLI
----
A Command Line Environment for connecting to EC2 instances through AWS EC2 Instance Connect.
"""
import os

__version__ = '1.0.1'

EnvironmentVariables = {
    'ca_bundle': ('ca_bundle', 'AWS_CA_BUNDLE', None, None),
    'output': ('output', 'AWS_DEFAULT_OUTPUT', 'json', None),
}


SCALAR_TYPES = set([
    'string', 'float', 'integer', 'long', 'boolean', 'double',
    'blob', 'timestamp'
])
COMPLEX_TYPES = set(['structure', 'map', 'list'])
