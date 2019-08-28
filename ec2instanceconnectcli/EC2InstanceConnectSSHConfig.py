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

class EC2InstanceConnectSSHConfig(object):
  """
  Generates a temporary ssh config file
  """
  def __init__(self, instance_bundles, logger):
    """
    :param instance_bundles: list of dicts that provide dns name, zone, etc information about EC2 instances
    :type instance_bundles: list
    :param logger: EC2 Instance Connect CLI logger to use for log messages
    :type logger: ec2instanceconnectcli.EC2InstanceConnectLogger.EC2InstanceConnectLogger
    """
    self.logger = logger
    self.instance_bundles = instance_bundles
    self.region = self.get_region()
    self.tempf = self.write_config()

  def get_region(self):
    region = None
    for bundle in self.instance_bundles:
      region = bundle['region']

    return region

  def add_instance_name(self):
    """
    Add ec2 instance id to ssh config
    """
    config = "host {0}\n".format(self.instance_bundles[0]['instance_id'])
    return config

  def add_ssm_proxy_command(self, config, region=None):
    """
    Add ProxyCommand to ssh config

    :param config: Initial config string
    :type config: basestring
    :param region: Region string
    :type region: basestring
    """

    region_cli = ''
    
    if region is not None:
      region_cli = "--region {0}".format(region)

    proxy_command = "ProxyCommand sh -c \"aws {0} ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'\"".format(region_cli)
    return "{0} {1}".format(config, proxy_command)

  def write_config(self):
    """
    Write ssh config file to temporary directory
    """
    config = self.add_instance_name()
    if self.instance_bundles[0]['ssm']:
      config = self.add_ssm_proxy_command(config, self.region)
    tempf = tempfile.NamedTemporaryFile(delete=False)
    with open(tempf.name, 'w') as f:
      f.write(config)
      os.chmod(tempf.name, 0o600)
    tempf.file.close()
    return tempf
    
  def get_config_file(self):
        """
        Returns temporary ssh config file.

        :return: ssh config filepath
        :rtype: basestring
        """
        return self.tempf.name
        
  def __del__(self):
        """
        Remove the temp ssh config file.
        """
        if self.tempf is not None:
          self.logger.debug('Deleting the ssh_config file: {0}'.format(self.tempf.name))
          os.remove(self.tempf.name)
