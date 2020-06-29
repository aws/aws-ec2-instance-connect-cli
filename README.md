# AWS EC2 Instance Connect CLI

This is a Python client for accessing EC2 instances via AWS EC2 Instance Connect.
This module supports Python 2.7.x and 3+.  [This package is available on PyPI for pip installation](https://pypi.org/project/ec2instanceconnectcli/), ie, `pip install ec2instanceconnectcli`

## Setup

It is strongly encouraged you set up a virtual environment for building and testing.

### Prerequisites

To set up this package you need to have pip installed.

### Package Setup

Install the package dependencies

`pip install -r requirements.txt`

## Running

Ensure your PYTHONPATH includes the package top-level directory.

Run the desired script with standard UNIX pathing.  For example,

`./bin/mssh ec2-user@ec2-54-245-189-134.us-west-2.compute.amazonaws.com -pr dev -t i-0b01816d5c99826d8 -z us-west-2a`

## Testing

Unit tests can be run with standard pytest.  They may be run, for example, by

`python -m pytest`

For Python2, ensure **mock** is installed: `pip2 install mock`.

Also, for corrcting import when using virtualenv, you have to export PYTHONPATH by running: `export PYTHONPATH=$(pwd)`

## Generating Documentation

Sphinx configuration has been included in this package.  To generate Sphinx documentation, run

`pip install -r requirements-docs.txt`

to pull dependencies.  Then, run

`sphinx-apidoc -o doc/source ec2instanceconnectcli`

to generate the module documentation reStructuredText files.  Finally, run

`sphinx-build ./doc/source [desired output directory]`

to generate the actual documentation html.
