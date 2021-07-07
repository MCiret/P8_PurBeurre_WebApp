import requests
import json
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from research.models import Food, Category


class Command(BaseCommand):
    help = 'Requests OFF API to get some foods to fill the database.'

    REQUESTED_FIELDS = ('_id', 'product_name', 'nutriscore_grade', 'url',
                        'image_front_url', 'image_nutrition_small_url', 'categories_tags')

    def handle(self, *args, **options):
        off_api_responses_list = []
        params_dict = Command.get_params_dict_from_json("research/management/off_research_params.json")
        for category in params_dict['categories']:
            resp = requests.get(Command.build_get_request(category, params_dict['page']))
            if resp.status_code == 200:
                resp_dict = resp.json()
                Command.save_foods_in_bd(resp_dict)
                off_api_responses_list.append(resp_dict)
        Command.update_json_page_number_param("research/management/off_research_params.json")
        ############################# Temporary data checking ################
        Command.write_valid_foods(off_api_responses_list)
        ######################################################################

    @staticmethod
    def get_params_dict_from_json(json_file: str) -> dict:
        with open(json_file, "r", encoding="utf-8") as file:
            params = json.load(file)
        return params

    @staticmethod
    def update_json_page_number_param(json_file: str):
        params = Command.get_params_dict_from_json("research/management/off_research_params.json")
        params["page"] = str(int(params["page"]) + 1)
        with open(json_file, "w", encoding="utf-8") as of:
            json.dump(params, of, indent=4, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def build_get_request(category, page_nb):
        return f"https://fr.openfoodfacts.org/cgi/search.pl?action=process" \
               f"&tagtype_0=categories" \
               f"&tag_contains_0=contains" \
               f"&tag_0={category}" \
               f"&fields={','.join(Command.REQUESTED_FIELDS)}" \
               f"&page_size=100&page={page_nb}&json=true"

    @staticmethod
    def save_foods_in_bd(off_api_resp_dict: 'dict[dict]'):
        for food in off_api_resp_dict["products"]:
            if Command.is_valid_food(food):
                Command.keep_max_three_food_categories(food["categories_tags"])
                tmp_food = Food(food["_id"], *list(food.values())[2:])
                tmp_food.save()
                for category in food["categories_tags"]:
                    tmp_cat = Category(name=category)
                    try:  # try to create this category in db...
                        tmp_cat.save()
                    except IntegrityError:  # ...if this category's name is already in db whereas it has to be unique
                        Category.objects.get(name=category).foods.add(tmp_food)
                    else:  # ...else just make the many-to-many relation
                        tmp_cat.foods.add(tmp_food)

    @staticmethod
    def is_valid_food(food_dict: dict) -> bool:
        """
        A valid product must have the REQUESTED_FIELDS (see the 'fields' parameter in build_get_request() above).
        """
        for field in Command.REQUESTED_FIELDS:
            if field not in food_dict.keys():
                return False
        return True

    @staticmethod
    def keep_max_three_food_categories(food_categories_list: list):
        if len(food_categories_list) > 3:
            del food_categories_list[3:]

    @staticmethod
    def write_valid_foods(off_api_json_responses: 'list[dict][dict]'):
        keeped_foods_list = [food for resp_dict in off_api_json_responses
                             for food in resp_dict["products"]
                             if Command.is_valid_food(food)]
        with open("final_products.json", "w", encoding="utf-8") as of:
            json.dump(keeped_foods_list, of, indent=4, sort_keys=True, ensure_ascii=False)
