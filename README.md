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

Details of some of the tasks above are explained more below.

### Rendering a Jinja Template: `render_template`

This task takes an example template using the [Jinja](https://palletsprojects.com/p/jinja/) templating system and renders it.
The example file used is located at `rendering_examples/template_rendering/main.md`.
The base file is written in the [Markdown](https://commonmark.org/) language.
It includes examples of using the `add_schema_table` hook to insert Schema 205 tables into markdown text.

The rendered result appears in `build/rendered_template/main.md`.


Development Workflow
--------------------

### Setting Up Schema 205 for Development

For those who wish to develop the Schema205 repository directly, we are using the [uv](https://docs.astral.sh/uv/getting-started/installation/) python package management and dependency tool.

Following are some considerations you should go through to configure your environment correctly for development and exploration.

1. **Install uv**

    Be sure to install [uv](https://docs.astral.sh/uv/getting-started/installation/) per the instructions from the uv website.

2. **Install dependencies**

    To install dependencies, go to the root folder of this repository and type:

    > uv sync

    This will install all of the normal and developer dependencies.
    If you have done this previously and there are no changes to the library versions being used, nothing will happen.

3. **Use the project**

    To run the various scripts and commands of the project, you can use the [DoIt!](https://pydoit.org/) file as follows:

    > uv run doit

    The first part of the command, `uv run`, uses uv to place the remaining part of the command within a Python virtual environment with all dependencies setup.
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

4. Ensure all *Toolkit 205* tests are passing locally (see the earlier section on setting up uv):

    ```
    doit run pytest
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
