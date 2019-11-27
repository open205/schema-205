Schema 205
===========

A JSON schema consistent with ASHRAE Standard 205.

**Disclaimer:** While this schema is developed in conjunction with the ASHRAE Standard 205 project committee, it is not an official ASHRAE product.

**Warning!**  As the proposed ASHRAE Standard 205P has not yet been published, the content in this repository is subject to change and should be considered unstable for application development.

Development Workflow
--------------------

*Schema 205* is developed as a submodule of [Toolkit 205](https://github.com/open205/toolkit-205). *Toolkit 205* is used to test the schema and example files. In general, one should only develop *Schema 205* in this context, where changes can be tested before being committed.

The general development workflow for making changes to Schema 205 are as follows:

1. Clone [Toolkit 205](https://github.com/open205/toolkit-205) and follow the instructions there to recursively clone or update the *Schema 205* submodule
2. Make a branch in the *Schema 205* submodule repository for your new changes
3. Make the necessary source code changes in both the *Toolkit 205* repository and the *Schema 205* submodule repository
4. Ensure all *Toolkit 205* tests are passing locally
5. Commit changes to the *Schema 205* submodule repository on its new branch
6. Push the changes to the *Schema 205* submodule repository
7. Perform any appropriate pull requests, merging, tagging, releasing steps in the *Schema 205* repository and checkout the final commit (or tag) in the *Schema 205* submodule repository
8. Commit any relevant changes to the *Toolkit 205* repository, including the new *Schema 205* submodule repository reference commit/tag in the *Toolkit 205* repository
9. Push the changes to the *Toolkit 205* repository
10. Allow the *Toolkit 205* repository CI to test the composite changes to both repositories on all platforms
11. Perform any appropriate pull requests, merging, tagging, releasing steps in the *Toolkit 205* repository
