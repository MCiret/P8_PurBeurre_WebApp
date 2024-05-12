from research.models import Food, Category
import itertools as it


def db_food_search(search_keywords: str = None, food_barcode: int = None):
    """
    Main function called by search.views.ResultView.get() method.
    """

    result = {
        "valid": None,
        "error": None,
        "data": {
            "search_keywords": search_keywords,
            "perfect_match" : None,
            "substitutes_foods": None
        }
    }

    # Get the user searched food :
    if search_keywords:
        look_for_foods_matching_user_search(search_keywords, result)
    elif food_barcode:
        result["valid"] = True
        result["data"]["perfect_match"] = Food.objects.get(barcode=food_barcode)

    if result["valid"] and result["data"]["perfect_match"]:
    # Get searched food's categories id
        food_categories_id = []
        for category in result["data"]["perfect_match"].category_set.all().order_by('categoryfoods__category_rank'):
            food_categories_id.append(Category.objects.filter(name=category.name).values('id')[0]['id'])

        # Get substitutes for the searched food
        result["data"]["substitutes_foods"] = look_for_substitutes(food_categories_id,
                                                       result["data"]["perfect_match"].nutri_score)

    return result


def look_for_foods_matching_user_search(search_keywords: str, result: dict) -> dict:
    """
    Look for food product matching the user's search keywords
    """
    searched_foods = Food.objects.filter(name__icontains=search_keywords)

    # If none food product matches the search keywords
    if len(searched_foods) == 0:
        result["valid"] = True
        if len(Food.objects.all()) == 0:
            result["valid"] = False
            result["error"] = "Empty DB"
    else:
        result["valid"] = True
        # if the search returns only 1 food (ideal case)
        if len(searched_foods) == 1:
            result["data"]["perfect_match"] = searched_foods[0]
        # else the search returns several foods
        else:
            result["data"]["several_matches"] = searched_foods


def look_for_substitutes(categories_id: list, nutriscore: str):
    """
    Substitutes search algorithm based on shared categories and nutriscore value.
    Substitutes are looked only for 2/3 of the searched food categories.
    These categories are ranked from the more specific to more general
    (see search/management/commands/filldb.py --> save_foods_in_db() for more infos about this ranking.
    """
    for cat_id in it.islice(categories_id, round(len(categories_id) / 3) * 2):
        substitutes = Food.objects.filter(category__id=cat_id, nutri_score__lt=nutriscore)
        if len(substitutes) > 0:
            return (substitutes)
        else:
            continue
    return None
