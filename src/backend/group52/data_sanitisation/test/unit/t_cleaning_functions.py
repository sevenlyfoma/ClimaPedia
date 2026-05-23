import unittest
import pandas as pd

from group52.data_sanitisation.lib import cleaning_functions


class TestMappingFunctions(unittest.TestCase):
    """Tests for functions ued by apply_string_mapaping"""

    # Tests for convert_to_float
    def test_convert_to_float_normal_data(self):
        """Test convert_to_float with normal data"""
        self.assertEqual(cleaning_functions.convert_to_float("10"), 10.0)
        self.assertEqual(cleaning_functions.convert_to_float("1"), 1.0)
        self.assertEqual(cleaning_functions.convert_to_float("35"), 35.0)
        self.assertEqual(cleaning_functions.convert_to_float("900"), 900.0)

    def test_convert_to_float_boundary_data(self):
        """Test convert_to_float with boundary data"""
        self.assertEqual(cleaning_functions.convert_to_float("0"), 0.0)
        self.assertEqual(cleaning_functions.convert_to_float("1.0"), 1.0)
        self.assertEqual(cleaning_functions.convert_to_float("-10"), -10.0)
        self.assertEqual(
            cleaning_functions.convert_to_float("92222222222222222222"),
            92222222222222222222.0,
        )

    def test_convert_to_float_error_data(self):
        """Test convert_to_float with error data"""
        self.assertEqual(cleaning_functions.convert_to_float(""), 0.0)
        self.assertEqual(cleaning_functions.convert_to_float("hello"), 0.0)

    # Tests for extract_q_code
    def test_extract_q_code_normal_data(self):
        """Test extract_q_code with normal data"""
        self.assertEqual(
            cleaning_functions.extract_q_code(
                "http://www.wikidata.org/entity/Q61021340"
            ),
            "Q61021340",
        )
        self.assertEqual(
            cleaning_functions.extract_q_code(
                "http://www.wikidata.org/entity/Q61207992"
            ),
            "Q61207992",
        )
        self.assertEqual(
            cleaning_functions.extract_q_code(
                "http://www.wikidata.org/entity/Q61308944"
            ),
            "Q61308944",
        )
        self.assertEqual(
            cleaning_functions.extract_q_code(
                "http://www.wikidata.org/entity/Q61282136"
            ),
            "Q61282136",
        )

    def test_extract_q_code_boundary_data(self):
        """Test extract_q_code with boundary data"""
        self.assertEqual(
            cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q1"), "Q1"
        )
        self.assertEqual(
            cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q0"), "Q0"
        )
        self.assertEqual(
            cleaning_functions.extract_q_code(
                "http://www.wikidata.org/entity/Q9000000000000000000000000000"
            ),
            "Q9000000000000000000000000000",
        )
        self.assertEqual(
            cleaning_functions.extract_q_code("http://www.wikidaQ61021340"), "Q61021340"
        )
        self.assertEqual(cleaning_functions.extract_q_code("xQ61021340"), "Q61021340")
        self.assertEqual(cleaning_functions.extract_q_code("Q61021340"), "Q61021340")
        self.assertEqual(cleaning_functions.extract_q_code("Q61021340XS"), "Q61021340")
        self.assertEqual(cleaning_functions.extract_q_code("Q61021340Q1"), "Q61021340")

    def test_extract_q_code_error_data(self):
        """Test extract_q_code with error data"""
        self.assertEqual(cleaning_functions.extract_q_code("1"), None)
        self.assertEqual(cleaning_functions.extract_q_code("Q"), None)
        self.assertEqual(cleaning_functions.extract_q_code(""), None)
        self.assertEqual(cleaning_functions.extract_q_code("hello world"), None)

    # Tests for reformat_lat_and_long
    def test_reformat_lat_and_long_normal_data(self):
        """Test reformat_lat_and_long with normal data"""
        self.assertEqual(cleaning_functions.reformat_lat_and_long("Point(1 1)"), "1 1")
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(1 -1)"), "1 -1"
        )
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(-1 1)"), "-1 1"
        )
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(-1 -1)"), "-1 -1"
        )

        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(70 30)"), "70 30"
        )
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(40 -56)"), "40 -56"
        )
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(-65 12)"), "-65 12"
        )
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(-14 -17)"), "-14 -17"
        )

    def test_reformat_lat_and_long_boundary_data(self):
        """Test reformat_lat_and_long with boundary data"""
        self.assertEqual(cleaning_functions.reformat_lat_and_long("Point(0 0)"), "0 0")
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(1110 11210)"), "1110 11210"
        )
        # self.assertEqual(cleaning_functions.reformat_lat_and_long("P(1 1)"), "1 1")
        # self.assertEqual(cleaning_functions.reformat_lat_and_long("(1 1)"), "1 1")
        self.assertEqual(
            cleaning_functions.reformat_lat_and_long("Point(1 1)xxxx"), "1 1"
        )

    def test_reformat_lat_and_long_error_data(self):
        """Test reformat_lat_and_long with error data"""
        self.assertEqual(cleaning_functions.reformat_lat_and_long(""), "0 0")
        self.assertEqual(cleaning_functions.reformat_lat_and_long("Point()"), "0 0")
        self.assertEqual(cleaning_functions.reformat_lat_and_long("Point(x y)"), "0 0")


class TestDataFrameOperations(unittest.TestCase):
    """Tests for cleaning functions that operate on data frames"""

    # Tests for drop_column
    def test_drop_column_normal(self):
        """Test drop_column drops a single column specified and no more"""
        d = {"col1": [1, 2], "col2": [3, 4]}
        df = pd.DataFrame(data=d)

        df = cleaning_functions.drop_column(df, "col1", [])

        self.assertFalse("col1" in list(df.columns))
        self.assertTrue("col2" in list(df.columns))

        df = cleaning_functions.drop_column(df, "col2", [])

        self.assertFalse("col1" in list(df.columns))
        self.assertFalse("col2" in list(df.columns))

    def test_drop_column_column_not_in_dataframe(self):
        """Test drop_column doesnt drop anything if the column isnt in the dataframe"""
        d = {"col1": [1, 2], "col2": [3, 4]}
        df = pd.DataFrame(data=d)

        df = cleaning_functions.drop_column(df, "col3", [])

        self.assertTrue("col1" in list(df.columns))
        self.assertTrue("col2" in list(df.columns))

    # Tests for extract_json_fields
    def test_extract_json_fields_extract_from_one_field_object(self):
        """test extract_json_fields when extracting a single field from an object with a single field"""
        d = [{"col1": {"x": 4}, "col2": {"x": 3}}]
        df = pd.DataFrame(data=d)

        df = cleaning_functions.extract_json_fields(df, "col1", ["x"])
        self.assertTrue("col1" in list(df.columns))
        self.assertTrue("col1_x" in list(df.columns))

    def test_extract_json_fields_extract_one_from_two_field_object(self):
        """test extract_json_fields when extracting a single field from an object with a two fields"""
        d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
        df = pd.DataFrame(data=d)

        df = cleaning_functions.extract_json_fields(df, "col1", ["y"])
        self.assertTrue("col1" in list(df.columns))
        self.assertTrue("col1_y" in list(df.columns))

    def test_extract_json_fields_extract_mutliple_fields(self):
        """test extract_json_fields when extracting a multiple fields from an object with multiple fields"""
        d = [{"col1": {"x": 4, "y": 6, "z": 8, "w": 2}, "col2": "3"}]
        df = pd.DataFrame(data=d)

        df = cleaning_functions.extract_json_fields(df, "col1", ["y", "z", "x"])
        self.assertTrue("col1" in list(df.columns))
        self.assertTrue("col1_x" in list(df.columns))
        self.assertTrue("col1_y" in list(df.columns))
        self.assertTrue("col1_z" in list(df.columns))
        self.assertFalse("col1_w" in list(df.columns))

    def test_extract_json_fields_extract_invalid_field(self):
        """test extract_json_fields when extracting an invalid field that nothing is extracted"""
        d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
        df = pd.DataFrame(data=d)

        df = cleaning_functions.extract_json_fields(df, "col1", ["z"])
        self.assertTrue("col1" in list(df.columns))
        self.assertFalse("col1_z" in list(df.columns))
        self.assertFalse("col1_x" in list(df.columns))
        self.assertFalse("col1_y" in list(df.columns))

    def test_extract_json_fields_extrac_no_field(self):
        """test extract_json_fields when extracting a blank field that nothing is extracted"""
        d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
        df = pd.DataFrame(data=d)

        df = cleaning_functions.extract_json_fields(df, "col1", [""])
        self.assertTrue("col1" in list(df.columns))
        self.assertFalse("col1_" in list(df.columns))
        self.assertFalse("col1_x" in list(df.columns))
        self.assertFalse("col1_y" in list(df.columns))

    # Tests for rename_column
    def test_rename_column_normal(self):
        """test that rename_column works under normal circumstances, old column gone, new column present"""
        d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
        df = pd.DataFrame(data=d)

        df = cleaning_functions.rename_column(df, "col1", ["newcol"])

        self.assertTrue("newcol" in list(df.columns))
        self.assertFalse("col1" in list(df.columns))

    def test_rename_column_too_many_args(self):
        """test extract_json_fields works when too many arguments are provided, ignoring the extra arguments"""
        d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
        df = pd.DataFrame(data=d)

        df = cleaning_functions.rename_column(df, "col1", ["newcol", "newcol2"])

        self.assertTrue("newcol" in list(df.columns))
        self.assertFalse("col1" in list(df.columns))
        self.assertFalse("newcol2" in list(df.columns))

    # TEsts for split_into_columns
    def test_split_into_columns_two_values_space(self):
        """test that split_into_columns works in the normal scenario of 2 values delimited by a space"""
        d = [{"col1": "6 5", "col2": "3"}, {"col1": "2 2", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.split_into_columns(df, "col1", [" ", "x", "y"])

        self.assertTrue("col1" in list(df.columns))
        self.assertTrue("x" in list(df.columns))
        self.assertTrue("y" in list(df.columns))

        self.assertEqual(df["x"].iloc[0], "6")
        self.assertEqual(df["y"].iloc[0], "5")

        self.assertEqual(df["x"].iloc[1], "2")
        self.assertEqual(df["y"].iloc[1], "2")

    def test_split_into_columns_two_values_comma(self):
        """test that split_into_columns works in the irregular scenario of 2 values delimited by a comma"""
        d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.split_into_columns(df, "col1", [",", "x", "y"])

        self.assertTrue("col1" in list(df.columns))
        self.assertTrue("x" in list(df.columns))
        self.assertTrue("y" in list(df.columns))

        self.assertEqual(df["x"].iloc[0], "6")
        self.assertEqual(df["y"].iloc[0], "5")

        self.assertEqual(df["x"].iloc[1], "2")
        self.assertEqual(df["y"].iloc[1], "2")

    def test_split_into_columns_three_values(self):
        """test that split_into_columns works in the irregular scenario of 3 values"""
        d = [{"col1": "6,5,5", "col2": "3"}, {"col1": "2,2,6", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.split_into_columns(df, "col1", [",", "x", "y", "z"])

        self.assertTrue("col1" in list(df.columns))
        self.assertTrue("x" in list(df.columns))
        self.assertTrue("y" in list(df.columns))
        self.assertTrue("z" in list(df.columns))

        self.assertEqual(df["x"].iloc[0], "6")
        self.assertEqual(df["y"].iloc[0], "5")
        self.assertEqual(df["z"].iloc[0], "5")

        self.assertEqual(df["x"].iloc[1], "2")
        self.assertEqual(df["y"].iloc[1], "2")
        self.assertEqual(df["z"].iloc[1], "6")

    def test_split_into_columns_too_many_columns(self):
        """test that split_into_columns doesnt change the dataframe if too many columns are provided"""
        d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.split_into_columns(df, "col1", [",", "x", "y", "z"])

        self.assertTrue("col1" in list(df.columns))
        self.assertFalse("x" in list(df.columns))
        self.assertFalse("y" in list(df.columns))
        self.assertFalse("z" in list(df.columns))

    def test_split_into_columns_too_few_columns(self):
        """test that split_into_columns doesnt change the dataframe if too few columns are provided"""
        d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.split_into_columns(df, "col1", [",", "x"])

        self.assertTrue("col1" in list(df.columns))
        self.assertFalse("x" in list(df.columns))

    # Tests for apply string mappings
    def test_apply_string_mappings_normal(self):
        """test that apply_string mappings works in the normal case"""
        d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.apply_string_mapping(df, "col2", ["convert_to_float"])

        self.assertEqual(df["col2"].iloc[0], 3.0)
        self.assertEqual(df["col2"].iloc[1], 4.0)

    def test_apply_string_mappings_invalid_function(self):
        """test that apply_string mappings doesnt throw an error with a non existant function"""

        d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.apply_string_mapping(df, "col2", ["hello"])

    def test_apply_string_mappings_valid_unworking_function(self):
        """test that apply_string mappings doesnt throw an error with a real but non functional function"""
        d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
        df = pd.DataFrame(data=d)
        df = cleaning_functions.apply_string_mapping(
            df, "col2", ["apply_string_mapping"]
        )


if __name__ == "__main__":
    unittest.main()
