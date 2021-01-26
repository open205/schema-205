# Example of Templating

This example uses the Python [Jinja](https://palletsprojects.com/p/jinja/)
project and the `add_table` hook.

We will insert a table here:

{{ add_table('ASHRAE205', 'data_types') }}

{## this is a comment ##}

See how easy it is!

To add a caption automatically to a table, just specify it in the call:

{{ add_table('ASHRAE205', 'data_types', caption='The Data Types Table') }}

If you would also like to have the `add_table` hook render a header for you, you can do that as well:

{{ add_table(
    'ASHRAE205',
    'data_types',
    caption='The Data Types Table',
    header_level_and_content=(3, "Data Types"))
}}


## Using Incorrect Parameters to Insert a Table

To insert a table, we need to provide the following:

- the schema file name (see `schema-source/*.schema.yaml` -- the name is the `*` part)
- the table type (one of `data_types`, `string_types`, `enumerations`, or `data_groups`)

If we specify those incorrectly, the rendered template will inform us with a friendly error message:

{{ add_table('nonexistingfile', 'data_types') }}

Or, if we specify a `table_type` value that doesn't exist, the system will also inform us:

{{ add_table('ASHRAE205', 'dolphin_types') }}


## Going Through the Remaining Table Types

We saw usage fo the `data_types` table already.
Here we run through the remaining table types with all options:


{{ add_table(
    'ASHRAE205',
    'string_types',
    caption='The String Types Table',
    header_level_and_content=(3, "String Types"))
}}

