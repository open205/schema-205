#!/usr/bin/env python

import os
from setuptools import setup

os.environ['PBR_VERSION'] = '0.1.0' # Stop-gap until https://bugs.launchpad.net/pbr/+bug/1675459 is fixed

build_path = os.path.join('.','build')
if not os.path.exists(build_path):
    os.mkdir(build_path)
lib_path = os.path.join(build_path,'lib')
if not os.path.exists(lib_path):
    os.mkdir(lib_path)

setup(
    setup_requires=['pbr'],
    pbr=True
)
