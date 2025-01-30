Schema 205
===========

A schema development package consistent with ASHRAE Standard 205.

This package is used to generate:

1. The normative JSON Schema for ASHRAE Standard 205
2. Schema documentation, and
3. Source code to read and process ASHRAE Standard 205 compliant representation data files.

Using DOIT Tasks!
-----------------

This repository ships with the [DoIt!](https://pydoit.org/) task automation tool.

The following DoIt! tasks are available:

- `doc`: Generates Markdown tables from common-schema
- `render_template`: Demonstrate how to render a template
- `schema`: Generates JSON schema from common-schema
- `test`: Performs unit tests and example file validation tests
- `validate`: Validates common-schema against meta-schema


Development Workflow
--------------------

### Setting Up Schema 205 for Development

For those who wish to develop the Schema205 repository directly, we are using the [Poetry](https://python-poetry.org/docs/#installation) python package management and dependency tool.

Following are some considerations you should go through to configure your environment correctly for development and exploration.

1. **Install Poetry**

    Be sure to install [Poetry](https://python-poetry.org/docs/#installation) per the instructions from the Poetry website.

2. **Install Python and support multiple Python versions on one machine**

    If you don't desire to support multiple versions of Python, then you need only ensure that you have at least one version of Python installed. This project requires Python 3.7 or higher. Please see the [Python Website](https://www.python.org/) for installation instructions for your operating system.

    If you wish to support multiple versions of Python during development, there are several options. One simple option is to just ensure you start up your command prompt (i.e., shell) with the Python version you wish to develop with.

    For something more sophisticated, we recommend [mini-conda](https://docs.conda.io/en/latest/miniconda.html), a free minimal installer for Conda. Conda is an open-source package and environment management system that runs on Windows, macOS, and Linux.  Use the following steps:

    a) [install mini-conda](https://docs.conda.io/en/latest/miniconda.html).

    b) [start conda](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda).  This will bring up a shell window that "knows" about conda capabilities.  Windows note: be sure to follow the recommended start procedure -- generally conda *cannot* be started from a native shell prompt (due to path issues).

    c) Create an environment for the version of Python you would like to use with Poetry and this project by typing the following at the conda shell:

    > (base) conda create -n py37 python=3.7

    Note: these environments persist between usage so you only need to create the environment once.

    This will create a conda environment named "py37" that only has Python 3.7 (and its dependencies) installed.
    If you want to use Python 3.9, you could type `conda create -n py39 python=3.9`, for example.
    The `-n` flag is short for the `--name` of the new conda environment.
    You have a lot of freedom for the names provided there are no spaces or exotic characters.
    The `python=3.7` part specifies that the new conda environment will use Python version 3.7.
    You can create as many environments with differing versions of Python as you desire.

    Once the desired environments are created, you can activate an environment by typing:

    > (base) conda activate py37

    When you are done with the environment, type:

    > (py37) conda deactivate

    ... or simply close your command shell when done.

    Once you've created the environment you desire, on subsequent use, you just need to start conda and activate the environment you want.

    Select the desired Python environment and activate it before proceeding to the next step.

3. **Install dependencies**

    To install dependencies, go to the root folder of this repository and type:

    > poetry install

    This will install all of the normal and developer dependencies.
    If you have done this previously and there are no changes to the library versions being used, nothing will happen.

4. **Using an editor**

    You can use any editor you desire to edit or explore the Python code and schema documents in our repository.

    We recommend [Visual Studio Code](https://code.visualstudio.com/) because of its strong Python integration.

    To get Visual Studio Code to work with Poetry, first follow steps 1-3 above.

    macOS: a) if you do not have command-line integration, [follow these instructions](https://code.visualstudio.com/docs/setup/mac#_launching-from-the-command-line), and restart your shell. b) follow steps 1-3.

    Windows: Follow steps 1-3 above.  The `code` command (see below) is already integrated into your shell.

    From within your running Python environment, type:

    > poetry shell

    This activates the virtual environment for Poetry.  Then enter:

    ```
    > cd toolkit-205/schema-205
    > code .
    ```

    This launches Visual Studio Code from within your Poetry environment.
    At the bottom left, choose the Python version you wish to use with the given environment.

    Open a terminal window TODO

    You're now ready to develop using Visual Studio Code!

5. **Use the project**

    To run the various scripts and commands of the project, you can use the [DoIt!](https://pydoit.org/) file as follows:

    > poetry run doit

    The first part of the command, `poetry run`, uses Poetry to place the remaining part of the command within a Python virtual environment with all dependencies setup.
    The second part of the command, `doit`, runs all of the tasks available in the `dodo.py` file.


### Developing with Toolkit 205

*Schema 205* is developed as a submodule of [Toolkit 205](https://github.com/open205/toolkit-205). *Toolkit 205* is used to test the schema and example files. In general, one should only develop *Schema 205* in this context, where changes can be tested before being committed.

The general development workflow for making changes to Schema 205 are as follows:

1. Clone [Toolkit 205](https://github.com/open205/toolkit-205) (or a fork if you don't have write access) and follow the instructions there to recursively clone or update the *Schema 205* submodule (and setup the project using the instructions in the [*Toolkit 205* README](https://github.com/open205/toolkit-205/blob/develop/README.md)):

    ```
    git clone --recurse-submodules https://github.com/open205/toolkit-205.git
    ```

2. Make a branch in the *Schema 205* submodule repository for your new changes:

    ```
    cd toolkit-205/schema-205
    git branch -b new-schema-branch-name
    ```

3. Make the necessary source code changes in both the *Toolkit 205* repository and the *Schema 205* submodule repository

4. Ensure all *Toolkit 205* tests are passing locally (see the earlier section on setting up Poetry):

    ```
    poetry run pytest
    ```

5. Commit changes to the *Schema 205* submodule repository on its new branch:

    ```
    git add -p  # Add your changes in hunks to staging
    git commit -m "Add description of changes to Schema 205."
    ```

6. Push the changes to the *Schema 205* submodule repository:

    ```
    git push --set-upstream origin new-schema-branch-name
    ```

7. Perform any appropriate pull request, merging, tagging, and/or releasing steps in the *Schema 205* repository (end here if no changes were made to *Toolkit 205*)

8. If changes were required in *Toolkit 205*, make a new branch and checkout the final *Schema 205* commit (or tag) in the *Schema 205* submodule repository

    ```
    cd ..  # back to toolkit directory
    git checkout -b new-toolkit-branch-name
    cd schema-205
    git pull
    git checkout final-schema-branch-name  # e.g., develop
    ```

9. Commit any relevant changes to the *Toolkit 205* repository, including the new *Schema 205* submodule repository reference commit/tag in the *Toolkit 205* repository:

    ```
    cd ..  # back again
    git add schema-205  # Update the commit toolkit 205 references
    git add -p  # Add your changes in hunks to staging
    git commit -m "Add description of changes to Toolkit 205."
    ```

10. Push the changes to the *Toolkit 205* repository:

    ```
    git push --set-upstream origin new-toolkit-branch-name
    ```

11. Allow the *Toolkit 205* repository CI to test the composite changes to both repositories on all platforms

12. Perform any appropriate pull request, merging, tagging, and releasing steps in the *Toolkit 205* repository
