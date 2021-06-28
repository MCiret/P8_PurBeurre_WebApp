from django.test import TestCase
from research.management.commands.fillbd import Command


class FilldbTests(TestCase):

    def test_build_request(self):
        fields = ("f1", "f2", "f3")

        bkup_requested_field = Command.REQUESTED_FIELDS
        Command.REQUESTED_FIELDS = fields

        self.assertEqual(Command.build_get_request("category"),
                         "https://fr.openfoodfacts.org/cgi/search.pl?action=process"
                         "&tagtype_0=categories"
                         "&tag_contains_0=contains"
                         "&tag_0=category"
                         "&fields=f1,f2,f3"
                         "&page_size=100&page=1&json=true")

        Command.REQUESTED_FIELDS = bkup_requested_field

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
