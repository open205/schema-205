# Example of Templating

This example uses the Python [Jinja](https://palletsprojects.com/p/jinja/)
project and the `add_table` hook.

We will insert a table here:

{{ add_table('ASHRAE205', 'data_types') }}

{## this is a comment ##}

See how easy it is!

## Using Incorrect Parameters to Insert a Table

To insert a table, we need to provide the following:

- the schema file name (see `schema-source/*.schema.yaml` -- the name is the `*` part)
- the table type (one of `data_types`, `string_types`, `enumerations`, or `data_groups`)

If we specify those incorrectly, the rendered template will inform us with a friendly error message:

{{ add_table('nonexistingfile', 'data_types') }}

Or, if we specify a `table_type` value that doesn't exist, the system will also inform us:

{{ add_table('ASHRAE205', 'dolphin_types') }}


