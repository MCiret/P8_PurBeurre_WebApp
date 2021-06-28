import requests
import json
from django.core.management.base import BaseCommand
from research.models import Food


class Command(BaseCommand):
    help = 'Requests OFF API to get some foods to fill the database.'

    RESEARCHED_CATEGORIES = ('biscuits', 'boissons', 'charcuteries', 'chocolats', 'fromages',
                             'epicerie', 'desserts', 'glaces', 'pains', 'plats_prepares',
                             'poissons', 'produits_laitiers', 'sauces', 'snacks', 'soupes',
                             'surgeles', 'viandes', 'yaourts')
    REQUESTED_FIELDS = ('_id', 'product_name', 'nutriscore_grade', 'url',
                        'image_front_url', 'image_nutrition_small_url', 'compared_to_category')

    def handle(self, *args, **options):
        off_api_responses_list = []
        for category in Command.RESEARCHED_CATEGORIES:
            resp = requests.get(Command.build_get_request(category))
            if resp.status_code == 200:
                resp_dict = resp.json()
                Command.save_valid_foods_in_bd(resp_dict)
                off_api_responses_list.append(resp_dict)
        ############################# Temporary data checking ################
        Command.write_valid_foods(off_api_responses_list)
        ######################################################################

    @staticmethod
    def build_get_request(category):
        return f"https://fr.openfoodfacts.org/cgi/search.pl?action=process" \
               f"&tagtype_0=categories" \
               f"&tag_contains_0=contains" \
               f"&tag_0={category}" \
               f"&fields={','.join(Command.REQUESTED_FIELDS)}" \
               f"&page_size=100&page=1&json=true"

    @staticmethod
    def save_valid_foods_in_bd(off_api_resp_dict: 'dict[dict]'):
        """
        A valid product = 7 requested fields (see the 'fields' parameter in build_get_request() above).
        """
        for food in off_api_resp_dict["products"]:
            if Command.is_valid_food(food):
                Food(*list(food.values())).save()

    @staticmethod
    def is_valid_food(food_dict: dict) -> bool:
        for field in Command.REQUESTED_FIELDS:
            if field not in food_dict.keys():
                return False
        return True

    @staticmethod
    def write_valid_foods(off_api_json_responses: 'list[dict][dict]'):
        keeped_foods_list = [food for resp_dict in off_api_json_responses
                             for food in resp_dict["products"]
                             if Command.is_valid_food(food)]
        with open("final_products.json", "w", encoding="utf-8") as of:
            json.dump(keeped_foods_list, of, indent=4, sort_keys=True, ensure_ascii=False)
