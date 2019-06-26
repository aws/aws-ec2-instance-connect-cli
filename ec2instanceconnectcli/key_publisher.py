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

import sys

def push_public_key(session, instance_id, user, pub_key, target_zone):
    """
    Creates a Boto3 client to make call to the EC2 Instance Connect Service and invokes the SendSSHPublicKey API

    :param session: A Botocore session to use to generate the boto client
    :type session: botocore.session.Session
    :param client_config: Contains AWS credentials, region and custom endpoint URL
    :type client_config: dict
    :param instance_id: Instance ID of the EC2 instance
    :type instance_id: basestring
    :param user: EC2 user to publish to on-instance
    :type user: basestring
    :param pub_key: Public key to be pushed
    :type pub_key: basestring
    :param target_zone: availability zone the instance lives in
    :type target_zone: basestring
    """

    try:
        client = session.create_client('ec2-instance-connect')
    except Exception as e:
        print("Error while trying to push the public key:\n" + str(e))
        sys.exit(1)

    params = {
              'InstanceId': instance_id,
              'InstanceOSUser': user,
              'SSHPublicKey': pub_key,
              'AvailabilityZone': target_zone
             }

    try:
        client.send_ssh_public_key(**params)
    except Exception as e:
        print("Error while pushing the public key:\n" + str(e))
        sys.exit(1)
