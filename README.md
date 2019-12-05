Schema 205
===========

A JSON schema consistent with ASHRAE Standard 205.

**Disclaimer:** While this schema is developed in conjunction with the ASHRAE Standard 205 project committee, it is not an official ASHRAE product.

**Warning!**  As the proposed ASHRAE Standard 205P has not yet been published, the content in this repository is subject to change and should be considered unstable for application development.

Development Workflow
--------------------

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

4. Ensure all *Toolkit 205* tests are passing locally:

    ```
    pipenv run pytest
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

10. Allow the *Toolkit 205* repository CI to test the composite changes to both repositories on all platforms

11. Perform any appropriate pull request, merging, tagging, and releasing steps in the *Toolkit 205* repository
