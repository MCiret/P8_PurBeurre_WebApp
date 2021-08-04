from research.models import Food, Category
import itertools as it


def researchs_in_db(research_keywords: str = None, food_barcode: int = None):
    """
    Main function called by research.views.ResultView.get() method.
    """

    # Get the user researched food :
    if research_keywords:
        result = look_for_foods_matching_user_research(research_keywords)
        # If none food matches the research keywords or if many foods match the research keywords
        if 'the_researched_food' not in result.keys():
            return result
    elif food_barcode:
        result = {'the_researched_food': Food.objects.get(barcode=food_barcode)}

    # Get researched food's categories id
    food_categories_id = []
    for category in result['the_researched_food'].category_set.all().order_by('categoryfoods__category_rank'):
        food_categories_id.append(Category.objects.filter(name=category.name).values('id')[0]['id'])

    # Get substitutes for the researched food
    result['substitutes_foods'] = look_for_substitutes(food_categories_id,
                                                       result['the_researched_food'].nutri_score)

    return result


def look_for_foods_matching_user_research(research_keywords: str) -> dict:
    """
    Look for food product matching the user's research keywords
    """
    researched_foods = Food.objects.filter(name__icontains=research_keywords)
    # If none food product matches the research keywords
    if len(researched_foods) == 0:
        return {
            'research_keywords': research_keywords,
        }
    else:
        # if the research returns only 1 food (ideal case)
        if len(researched_foods) == 1:
            return {
                'the_researched_food': researched_foods[0],
            }
        # else the research returns several foods
        else:
            return {
                'research_keywords': research_keywords,
                'many_researched_foods': researched_foods,
            }


def look_for_substitutes(categories_id: list, nutriscore: str):
    """
    Substitutes research algorithm based on shared categories and nutriscore value.
    Substitutes are looked only for 2/3 of the researched food categories.
    These categories are ranked from the more specific to more general
    (see research/management/commands/filldb.py --> save_foods_in_db() for more infos about this ranking.
    """
    for cat_id in it.islice(categories_id, round(len(categories_id) / 3) * 2):
        substitutes = Food.objects.filter(category__id=cat_id, nutri_score__lt=nutriscore)
        if len(substitutes) > 0:
            return (substitutes)
        else:
            continue
    return None
