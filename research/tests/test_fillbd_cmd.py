from django.test import TestCase
from unittest import mock
from research.management.commands.filldb import Command
import json
import tempfile


class FilldbTests(TestCase):

    def test_build_request(self):
        with mock.patch.object(Command, 'REQUESTED_FIELDS', new_callable=mock.PropertyMock) as mock_fields:
            mock_fields.return_value = ("f1", "f2", "f3")

            self.assertEqual(Command.build_get_request("category", "page_nb"),
                         "https://fr.openfoodfacts.org/cgi/search.pl?action=process"
                         "&tagtype_0=categories"
                         "&tag_contains_0=contains"
                         "&tag_0=category"
                         "&fields=f1,f2,f3"
                         "&page_size=100&page=page_nb&json=true")

    def test_is_valid_food(self):
        food_dict_valid = {
            "f1": "val1",
            "f2": "val2",
            "f3": "val3",
            "f4": "val4",
        }
        food_dict_not_valid = {
            "f1": "val1",
            "f3": "val3",
            "f4": "val4",
        }
        fields = ("f1", "f2", "f3", "f4")

        bkup_requested_field = Command.REQUESTED_FIELDS
        Command.REQUESTED_FIELDS = fields

        self.assertTrue(Command.is_valid_food(food_dict_valid))
        self.assertFalse(Command.is_valid_food(food_dict_not_valid))

        Command.REQUESTED_FIELDS = bkup_requested_field

    def test_keep_max_three_food_categories(self):
        long_cat_list = ["c1", "c2", "c3", "c4", "c5"]
        exact_cat_list = ["c1", "c2", "c3"]
        short_cat_list = ["c1", "c2"]
        Command.keep_max_three_food_categories(long_cat_list)
        Command.keep_max_three_food_categories(exact_cat_list)
        Command.keep_max_three_food_categories(short_cat_list)
        self.assertListEqual(long_cat_list, ["c1", "c2", "c3"])
        self.assertListEqual(exact_cat_list, ["c1", "c2", "c3"])
        self.assertListEqual(short_cat_list, ["c1", "c2"])

    def test_get_params_dict_from_json(self):
        read_data = json.dumps({
            "categories": ["c1", "c2", "c3", "c4"],
            "page": "nb"
        })
        mock_open_file = mock.mock_open(read_data=read_data)
        with mock.patch('builtins.open', mock_open_file):
            res = Command.get_params_dict_from_json("json_file")
        self.assertEqual(res, {
            "categories": ["c1", "c2", "c3", "c4"],
            "page": "nb"
        })

    @mock.patch("research.management.commands.filldb.Command.get_params_dict_from_json")
    def test_update_json_page_number_param(self, mock_get_param):
        mock_get_param.return_value = {
            "categories": ["c1", "c2", "c3", "c4"],
            "page": "1"
        }
        outfile_path = tempfile.mkdtemp()[1]
        Command.update_json_page_number_param(outfile_path)
        with open(outfile_path, "r", encoding="utf-8") as file:
            res = json.load(file)
        self.assertEqual(res, {
            "categories": ["c1", "c2", "c3", "c4"],
            "page": "2"
        })
