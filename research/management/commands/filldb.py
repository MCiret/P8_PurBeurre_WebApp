import requests
import json
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from research.models import Food, Category


class Command(BaseCommand):
    """ $ py(thon) manage.py filldb """

    help = 'Requests OFF API to get some foods to fill the database.'

    REQUESTED_FIELDS = ('_id', 'product_name', 'nutriscore_grade', 'url',
                        'image_front_url', 'image_nutrition_url', 'categories_tags')

    def handle(self, *args, **options):
        """ Personalized command to run the OFF API requests and the database filling """
        off_api_responses_list = []  # Temporary data checking TO DELETE ################
        params_dict = Command.get_params_dict_from_json("research/management/off_research_params.json")
        for category in params_dict['categories']:
            resp = requests.get(Command.build_get_request(category, params_dict['page']))
            if resp.status_code == 200:
                resp_dict = resp.json()
                Command.save_foods_in_db(resp_dict)
                off_api_responses_list.append(resp_dict)  # Temporary data checking TO DELETE ################
        Command.update_json_page_number_param("research/management/off_research_params.json")
        ############################# Temporary data checking TO DELETE ################
        Command.write_valid_foods(off_api_responses_list)
        ######################################################################

    @staticmethod
    def get_params_dict_from_json(json_file: str) -> dict:
        """ Get from json file parameters used for OFF API requests """
        with open(json_file, "r", encoding="utf-8") as file:
            params = json.load(file)
        return params

    @staticmethod
    def update_json_page_number_param(json_file: str):
        """
            Parameter page number for OFF API requests is incremented after each run of filldb command,
            to add more foods in db...
        """
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
    def save_foods_in_db(off_api_resp_dict: dict):
        for food_dict in off_api_resp_dict["products"]:
            if Command.is_valid_food(food_dict):
                food = Food(food_dict["_id"], *list(food_dict.values())[2:])
                try:
                    food.save()
                except IntegrityError:
                    pass
                # Ranks categories_tags from the most general to the most specific
                # (see OFF API json response structure) :
                for i, category in enumerate(reversed(food_dict["categories_tags"])):
                    cat = Category(name=category)
                    # try to create this category in db...
                    try:
                        cat.save()
                    # ...if this category's name is already in db (whereas it has to be unique),
                    # just select this category and make the food relation :
                    except IntegrityError:
                        Category.objects.get(name=category).foods.add(food, through_defaults={'category_rank': i+1})
                    # ...else the new category had been inserted then make the food relation :
                    else:
                        cat.foods.add(food, through_defaults={'category_rank': i+1})

    @staticmethod
    def is_valid_food(food_dict: dict) -> bool:
        """
        A valid product has to respect 2 conditions :
        1) have all REQUESTED_FIELDS (class attribute),
        2) have at least 3 categories (because of look_for_substitutes() in research/substitutes_research.py).

        """
        for field in Command.REQUESTED_FIELDS:
            if field not in food_dict.keys():
                return False
        if len(food_dict['categories_tags']) < 3:
            return False
        return True

    ####################### Temporary data checking TO DELETE ################
    @staticmethod
    def write_valid_foods(off_api_json_responses: 'list[dict][dict]'):
        keeped_foods_list = [food for resp_dict in off_api_json_responses
                             for food in resp_dict["products"]
                             if Command.is_valid_food(food)]
        with open("final_products.json", "w", encoding="utf-8") as of:
            json.dump(keeped_foods_list, of, indent=4, sort_keys=True, ensure_ascii=False)
    ###########################################################################