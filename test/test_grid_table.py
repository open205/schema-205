"""
Test aspects of the grid table maker.
"""
import schema205.md.grid_table as table


EXPECTED_1 = """
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| **Name**                               | **Description** | **Data Type**                  | **Units** | **Range** | **Notes**        |
+========================================+=================+================================+===========+===========+==================+
| manufacturer                           | Manufacturer    | String                         |           |           |                  |
|                                        | name            |                                |           |           |                  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| manufacturer_software_version          | Version of the  | String                         |           |           |                  |
|                                        | software used   |                                |           |           |                  |
|                                        | to generate the |                                |           |           |                  |
|                                        | performance map |                                |           |           |                  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| model_number                           | Model number    | Pattern                        |           |           | Pattern shall    |
|                                        |                 |                                |           |           | match all model  |
|                                        |                 |                                |           |           | numbers that can |
|                                        |                 |                                |           |           | be represented   |
|                                        |                 |                                |           |           | by the           |
|                                        |                 |                                |           |           | *representation* |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| nominal_voltage                        | Unit nominal    | Numeric                        | V         | ≥ 0       | If the unit can  |
|                                        | voltage         |                                |           |           | operate at       |
|                                        |                 |                                |           |           | multiple         |
|                                        |                 |                                |           |           | voltages, the    |
|                                        |                 |                                |           |           | lower of the two |
|                                        |                 |                                |           |           | shall be stated  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| nominal_frequency                      | Unit nominal    | Numeric                        | Hz        | ≥ 0       | Power supply     |
|                                        | frequency       |                                |           |           | frequency for    |
|                                        |                 |                                |           |           | the intented     |
|                                        |                 |                                |           |           | region of        |
|                                        |                 |                                |           |           | installation     |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| tolerance_standard                     | Name and        | String                         |           |           | Example: AHRI    |
|                                        | version of the  |                                |           |           | 550/590-2015,    |
|                                        | testing or      |                                |           |           | EN14511-2018,    |
|                                        | certification   |                                |           |           | EN14825-2016,    |
|                                        | standard under  |                                |           |           | GB18430.1-2007   |
|                                        | which the       |                                |           |           |                  |
|                                        | chiller is      |                                |           |           |                  |
|                                        | rated           |                                |           |           |                  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| compressor_type                        | Type of         | \\<CompressorType\\>             |           |           |                  |
|                                        | compressor      |                                |           |           |                  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| speed_control_type                     | Type of         | \\<CompressorSpeedControlType\\> |           |           |                  |
|                                        | compressor      |                                |           |           |                  |
|                                        | speed control   |                                |           |           |                  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| liquid_data_source                     | Source of the   | String                         |           |           | Example: "ASHRAE |
|                                        | liquid          |                                |           |           | Handbook         |
|                                        | properties data |                                |           |           | Fundamentals     |
|                                        |                 |                                |           |           | 2013 chapter 31" |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| refrigerant_type                       | Refrigerant     | \\<RefrigerantType\\>            |           |           |                  |
|                                        | used in the     |                                |           |           |                  |
|                                        | chiller         |                                |           |           |                  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
| hotgas_bypass_installed                | Indicates if a  | Boolean                        |           |           |                  |
|                                        | hot-gas bypass  |                                |           |           |                  |
|                                        | valve is        |                                |           |           |                  |
|                                        | installed on    |                                |           |           |                  |
|                                        | the chiller     |                                |           |           |                  |
+----------------------------------------+-----------------+--------------------------------+-----------+-----------+------------------+
""".strip()


def test_rendering_no_1():
    d = {
            'Name': [
                'manufacturer',
                'manufacturer_software_version',
                'model_number',
                'nominal_voltage',
                'nominal_frequency',
                'tolerance_standard',
                'compressor_type',
                'speed_control_type',
                'liquid_data_source',
                'refrigerant_type',
                'hotgas_bypass_installed',
                ],
            'Description': [
                'Manufacturer name',
                'Version of the software used to generate the performance map',
                'Model number',
                'Unit nominal voltage',
                'Unit nominal frequency',
                'Name and version of the testing or certification standard under which the chiller is rated',
                'Type of compressor',
                'Type of compressor speed control',
                'Source of the liquid properties data',
                'Refrigerant used in the chiller',
                'Indicates if a hot-gas bypass valve is installed on the chiller',
                ],
            'Data Type': [
                'String',
                'String',
                'Pattern',
                'Numeric',
                'Numeric',
                'String',
                '\\<CompressorType\\>',
                '\\<CompressorSpeedControlType\\>',
                'String',
                '\\<RefrigerantType\\>',
                'Boolean',
                ],
            'Units': [
                '',
                '',
                '',
                'V',
                'Hz',
                '',
                '',
                '',
                '',
                '',
                '',
                ],
            'Range': [
                '',
                '',
                '',
                '≥ 0',
                '≥ 0',
                '',
                '',
                '',
                '',
                '',
                '',
                ],
            'Req': [
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                ],
            'Notes': [
                '',
                '',
                'Pattern shall match all model numbers that can be represented by the *representation*',
                'If the unit can operate at multiple voltages, the lower of the two shall be stated',
                'Power supply frequency for the intented region of installation',
                'Example: AHRI 550/590-2015, EN14511-2018, EN14825-2016, GB18430.1-2007',
                '',
                '',
                'Example: "ASHRAE Handbook Fundamentals 2013 chapter 31"',
                '',
                '',
                ],
            }
    actual = table.make_table_from_dict_of_arrays(
            d,
            columns=['Name', 'Description', 'Data Type', 'Units', 'Range', 'Req', 'Notes'],
            preferred_sizes=[40] + [0]*6,
            ).strip()
    assert actual == EXPECTED_1


def test_wrap_text_to_lines():
    s = "Mares eat oats and does eat oats and little lambs eat ivy"
    expected = [
        #012345678901
        " Mares eat ",
        " oats and ",
        " does eat ",
        " oats and ",
        " little ",
        " lambs eat ",
        " ivy ",
        ]
    actual = table.wrap_text_to_lines(s, 12)
    assert expected == actual


def test_wrap_text_to_lines_with_newlines():
    expected = [" a ", " b ", " c "]
    actual = table.wrap_text_to_lines("a\nb\nc", 3)
    assert expected == actual