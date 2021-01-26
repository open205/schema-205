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
- the `table_type` (one of `data_types`, `string_types`, `enumerations`, or `data_groups`)
- the `item_type` which is required for `enumerations` and `data_groups`

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

The `enumerations` and `data_groups` tables require specifying an `item_type` to retrieve the correct table.

{{ add_table(
    'ASHRAE205',
    'enumerations',
    item_type='ASHRAE205Version',
    caption='ASHRAE 205 Versions',
    header_level_and_content=(3, "ASHRAE 205 Version"))
}}

The `item_type` value is used to pull out the correct table from all of the potential enumerations tables.
If we don't specify it or specify it wrong, we get a helpful error message listing the possible `item_type` options:

{{ add_table(
    'ASHRAE205',
    'enumerations',
    item_type="we_do_not_know",
    caption="When we don't know the item type...",
    header_level_and_content=(3, "We Don't Know What Item Type to Choose..."))
}}

The `data_groups` table operates similar to enumerations:

{{ add_table(
    'ASHRAE205',
    'data_groups',
    item_type='LiquidMixture',
    caption='Liquid mixtures',
    header_level_and_content=(3, "Available Liquid Mixture Options"))
}}

Similar to the `enumerations` table, if we don't know what `item_type` value to choose, we can leave it blank and let the system respond with all of the options in an error message:

{{ add_table('ASHRAE205', 'data_groups', item_type="") }}

