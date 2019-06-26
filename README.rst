=============
ec2-connect-cli
=============

This is a Python client for accessing EC2 instances via AWS EC2 Managed SSH.  This client generates a short-lived RSA
keypair and pushes it through the AWS Managed SSH service, then uses the key to connect to the target EC2 instance.

This client supports all standard ssh operations with the `mssh` command and all standard sftp operations with the
`msftp` command.

The ec2-connect-cli package works on Python versions:

* 2.6.x and greater
* 2.7.x and greater
* 3.3.x and greater
* 3.4.x and greater
* 3.5.x and greater
* 3.6.x and greater

------------
Installation
------------

The easiest way to install ec2-connect-cli is to use `pip`_::

    $ pip install ec2instanceconnectcli

or, if you are not installing in a ``virtualenv``::

    $ sudo pip install ec2instanceconnectcli

If you have the ec2-connect-cli installed and want to upgrade to the latest version you can run::

    $ pip install --upgrade ec2instanceconnectcli

This will install the ec2instanceconnectcli package as well as all dependencies.  Once you have the ec2instanceconnectcli
directory structure on your workstation, you can just run::

    $ cd <path_to_ec2instanceconnectcli>
    $ python setup.py install

---------------
Getting Started
---------------

Before using ec2-connect-cli, you need to tell it about your AWS credentials.  This can be done in the same way
as you would configure `aws-cli`_

^^^^^^^^
Examples
^^^^^^^^

Connect to an instance and open a shell

    $ mssh [instance id]

Connect to an instance by DNS name as user "my-user" and run the command "ls"

    $ mssh my-user@ec2-[ec2 IP].us-east-1.compute.amazonaws.com -t [instance id] ls

Run sftp against instance using the AWS CLI profile "otherprofile" and transferring my-file

    $ msftp -pr otherprofile [instance id]:my-file

.. _pip: http://www.pip-installer.org/en/latest/
.. _aws-cli: https://github.com/aws/aws-cli
