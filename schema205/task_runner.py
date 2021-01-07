"""
This module provides a programmatic interface to run tasks from the dodo.py
file in the root directory.

This module custom loads the dodo.py module which is kept at the root of the project.
Then, it provides a thin interface over the doit tasks in that module.
"""
import sys
import os

from doit.cmd_base import ModuleTaskLoader
from doit.doit_cmd import DoitMain

# Modify System Path so we can load dodo.py in root directory
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, PARENT_DIR)

import dodo


def run_task(task_args):
    """
    - task_args: array of string, the arguments to `doit run`
    """
    sys.exit(
        DoitMain(
            ModuleTaskLoader(dodo)).run(task_args))


def build():
    """
    Run dodo.py: all tasks
    equivalent to `dodo run`
    """
    run_task([])


def validate():
    """
    equivalent to `dodo run validate`
    """
    run_task(["validate"])


def doc():
    """
    equivalent to `dodo run doc`
    """
    run_task(["doc"])


def schema():
    """
    equivalent to `dodo run schema`
    """
    run_task(["schema"])


if __name__ == "__main__":
    build()
