#!/usr/bin/env python

import os
from setuptools import setup

os.environ['PBR_VERSION'] = '0.1.0' # Stop-gap until https://bugs.launchpad.net/pbr/+bug/1675459 is fixed

setup(
    setup_requires=['pbr'],
    pbr=True
)
