from research.models import Food, Category
from django.db.models import QuerySet
import itertools as it


def researchs_in_db(research_keywords: str = None, food_barcode: int = None):

    if research_keywords:
        result = look_for_foods_matching_user_research(research_keywords)
        if 'the_researched_food' not in result.keys():
            return result
    elif food_barcode:
        result = {'the_researched_food': Food.objects.get(barcode=food_barcode)}

    # Get food's categories id
    food_categories_id = []
    for category in result['the_researched_food'].category_set.all().order_by('categoryfoods__category_rank'):
        food_categories_id.append(Category.objects.filter(name=category.name).values('id')[0]['id'])

    result['substitutes_foods'] = look_for_substitutes(food_categories_id,
                                                       result['the_researched_food'].nutri_score)

    # TEMPORARY (to delete!) ######################################################################
    add_food_categories(result['the_researched_food'])
    add_food_categories(result['substitutes_foods'])
    ###############################################################################################
    return result


def look_for_foods_matching_user_research(research_keywords: str) -> dict:
    researched_foods = Food.objects.filter(name__icontains=research_keywords)
    if len(researched_foods) == 0:
        return {
            'research_keywords': research_keywords,
        }
    else:
        if len(researched_foods) == 1:  # if the research returns only 1 food
            return {
                'the_researched_food': researched_foods[0],
            }
        else:  # else the research returns several foods, the user will have to choose 1
            return {
                'research_keywords': research_keywords,
                'many_researched_foods': researched_foods,
            }


def look_for_substitutes(categories_id: list, nutriscore: str):
    # try 2/3 of the top of food's categories (which are ranked)
    for cat_id in it.islice(categories_id, round(len(categories_id) / 3) * 2):
        substitutes = Food.objects.filter(category__id=cat_id, nutri_score__lt=nutriscore)
        if len(substitutes) > 0:
            return (substitutes)
        else:
            continue
    return None


# TEMPORARY (to delete!) #####################################################################
def add_food_categories(food: Food):
    if isinstance(food, Food):
        food.categories = list(food.category_set.all().order_by('categoryfoods__category_rank'))
    elif isinstance(food, QuerySet):
        for f in food:
            f.categories = list(f.category_set.all().order_by('categoryfoods__category_rank'))
    return food
###############################################################################################
