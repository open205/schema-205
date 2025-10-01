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

- `generate_markdown`: Generates Markdown tables from common-schema
- `generate_web_docs`: Generates web documentation from templates
- `generate_meta_schemas`: Generates validation files for common-schema
- `generate_json_schemas`: Generates JSON schema from common-schema
- `validate_schemas`: Validates common-schema against meta-schema
- `generate_cpp_project`: Generates header and source files, with basic CMake build integration


Development Workflow
--------------------

### Setting Up Schema 205 for Development

For those who wish to develop the Schema205 repository directly, we are using the [Poetry](https://python-poetry.org/docs/#installation) python package management and dependency tool.

Following are some considerations you should go through to configure your environment correctly for development and exploration.

1. **WIP: Using uv to install the package and dependencies**
1. **Using an editor**

    You can use any editor you desire to edit or explore the Python code and schema documents in our repository.

    We recommend [Visual Studio Code](https://code.visualstudio.com/) because of its strong Python integration.

    1. From a command shell
    1. From inside VS Code

1. **Use the project**

    WIP: doit instructions


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
