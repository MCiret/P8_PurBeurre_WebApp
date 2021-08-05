from django.test import TestCase, TransactionTestCase
from unittest import mock
from research.management.commands.filldb import Command
from research.models import Food, Category
import json
import tempfile


class FilldbTestsExceptSQL(TestCase):
    """ Tests everything except database queries parts which are mocked """

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

    @mock.patch('research.management.commands.filldb.Command.REQUESTED_FIELDS', new_callable=mock.PropertyMock)
    def test_build_request(self, mock_fields):
        mock_fields.return_value = ("f1", "f2", "f3")

        self.assertEqual(Command.build_get_request("category", "page_nb"),
                         "https://fr.openfoodfacts.org/cgi/search.pl?action=process"
                         "&tagtype_0=categories"
                         "&tag_contains_0=contains"
                         "&tag_0=category"
                         "&fields=f1,f2,f3"
                         "&page_size=50&page=page_nb&json=true")

    @mock.patch('research.management.commands.filldb.Command.REQUESTED_FIELDS', new_callable=mock.PropertyMock)
    def test_is_valid_food(self, mock_fields):
        mock_fields.return_value = ("f1", "f2", "f3", "f4", 'categories_tags')

        valid_food_dict = {
            "f1": "val1",
            "f2": "val2",
            "f3": "val3",
            "f4": "val4",
            'categories_tags': ["c1", "c2", "c3"]
        }
        invalid_food_dict_one_field_missing = {
            "f1": "val1",
            "f2": "val2",
            "f3": "val3",
            "f4": "val4",
        }
        invalid_food_dict_less_than_3_categories = {
            "f1": "val1",
            "f2": "val2",
            "f3": "val3",
            "f4": "val4",
            'categories_tags': ["c1", "c2"]
        }

        self.assertTrue(Command.is_valid_food(valid_food_dict))
        self.assertFalse(Command.is_valid_food(invalid_food_dict_one_field_missing))
        self.assertFalse(Command.is_valid_food(invalid_food_dict_less_than_3_categories))

    @mock.patch("research.management.commands.filldb.Command.get_params_dict_from_json")
    @mock.patch("research.management.commands.filldb.Command.build_get_request")
    @mock.patch('requests.get')
    @mock.patch("research.management.commands.filldb.Command.save_foods_in_db")
    @mock.patch("research.management.commands.filldb.Command.update_json_page_number_param")
    def test_my_handle_command_filldb_if_api_resp_is_ok(self, mock_update, mock_save, mock_get,
                                                        mock_build, mock_get_params):
        mock_get.return_value.status_code = 200
        mock_get_params.return_value = {
            "categories": ["c1", "c2", "c3", "c4"],
            "page": "1"
        }

        cmd = Command()
        cmd.handle()
        self.assertTrue(mock_save.called)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_build.called)
        self.assertTrue(mock_get_params.called)
        self.assertTrue(mock_update.called)

    @mock.patch("research.management.commands.filldb.Command.get_params_dict_from_json")
    @mock.patch("research.management.commands.filldb.Command.build_get_request")
    @mock.patch('requests.get')
    @mock.patch("research.management.commands.filldb.Command.save_foods_in_db")
    @mock.patch("research.management.commands.filldb.Command.update_json_page_number_param")
    def test_my_handle_command_dont_filldb_if_api_resp_is_not_ok(self, mock_update, mock_save, mock_get,
                                                                 mock_build, mock_get_params):
        mock_get.return_value.status_code = 400
        mock_get_params.return_value = {
            "categories": ["c1", "c2", "c3", "c4"],
            "page": "1"
        }

        cmd = Command()
        cmd.handle()
        self.assertFalse(mock_save.called)
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_build.called)
        self.assertTrue(mock_get_params.called)
        self.assertTrue(mock_update.called)


class FilldbTests(TransactionTestCase):
    """ Tests only database queries """

    @mock.patch("research.management.commands.filldb.Command.is_valid_food")
    def test_sql_in_save_foods_in_db_method(self, mock_is_valid_food):

        mock_is_valid_food.return_value = True

        with open("research/tests/mock_off_api_response.json", "r", encoding="utf-8") as json_file:
            off_api_resp_dict = json.load(json_file)

        Command.save_foods_in_db(off_api_resp_dict)

        all_foods_in_db = Food.objects.all()
        self.assertEqual(len(all_foods_in_db), 2)

        all_categories_in_db = Category.objects.all()
        self.assertEqual(len(all_categories_in_db), 11)

        gazpacho_food = all_foods_in_db[0]
        self.assertEqual(gazpacho_food.barcode, "5410188031072")  # see research/tests/mock_off_api_response.json

        gazpacho_food_categories_list = [cat.name for cat in gazpacho_food.category_set
                                                                          .all()
                                                                          .order_by('categoryfoods__category_rank')]
        self.assertEqual(gazpacho_food_categories_list,
                         ["en:refrigerated-soups", "en:gazpacho", "en:refrigerated-meals",
                          "en:cold-soups", "en:vegetable-soups", "en:meals"])
        # see research/tests/mock_off_api_response.json
