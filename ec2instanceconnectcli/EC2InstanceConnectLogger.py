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

import logging

class EC2InstanceConnectLogger(object):
    """
    Common logger for all the EC2InstanceConnect components.
    """

    def __init__(self, debug=False):
        """
        :param debug: Specifies if debug messages should be enabled
        :type debug: bool
        """
        self.logger = logging.getLogger('EC2InstanceConnect')
        log_level = logging.ERROR
        if debug:
            log_level = logging.DEBUG
        self.logger.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch) 

    def get_logger(self):
        return self.logger
