#!/usr/bin/env python
import codecs
import os.path
import re
import sys
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = ['cryptography>=39.0.1',
            'botocore>=1.12.179'
            ]

setup_options = dict(
    name='ec2instanceconnectcli',
    version=find_version('ec2instanceconnectcli', '__init__.py'),
    description='Command Line Interface for AWS EC2 Instance Connect',
    long_description='This CLI package handles publishing keys through EC2 Instance Connect'
                     'and using them to connect to EC2 instances.',
    author='Amazon Web Services',
    url='https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Connect-using-EC2-Instance-Connect.html',
    scripts=['bin/mssh', 'bin/msftp', 'bin/mssh.cmd', 'bin/msftp.cmd',
        'bin/mssh-putty.cmd', 'bin/msftp-putty.cmd'],
    packages=find_packages(exclude=['test']),
    package_data={},
    install_requires=requires,
    license='Apache License 2.0',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: File Transfer Protocol (FTP)',
        'Topic :: System :: Systems Administration :: Authentication/Directory'
    )
)

setup(**setup_options)
