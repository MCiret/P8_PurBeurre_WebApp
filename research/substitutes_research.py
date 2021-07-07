from research.models import Food, Category
from django.db.models import QuerySet
import itertools as itert


def look_for_substitutes(research_keywords: str = None, food_barcode: int = None):
    if research_keywords:
        result = look_for_foods_matching_user_research(research_keywords)
        if 'the_researched_food' not in result.keys():
            return result
    elif food_barcode:
        result = {'the_researched_food': Food.objects.get(barcode=food_barcode)}
    # Get food's categories id
    food_categories_id = []
    for category in result['the_researched_food'].category_set.all():
        food_categories_id.append(Category.objects.filter(name=category.name).values('id')[0]['id'])

    result['substitutes_foods'] = get_relevant_substitutes(food_categories_id,
                                                           result['the_researched_food'].nutri_score)
    add_food_categories(result['the_researched_food'])
    add_food_categories(result['substitutes_foods'])
    return result


def look_for_foods_matching_user_research(research_keywords: str) -> dict:
    researched_foods = Food.objects.filter(name__icontains=research_keywords)
    if len(researched_foods) == 0:
        return {
            'research_key_words': research_keywords,
        }
    else:
        if len(researched_foods) == 1:  # if the research returns only 1 food
            return {
                'the_researched_food': researched_foods[0],
            }
        else:  # else the research returns several foods, the user will have to choose 1
            return {
                'research_key_words': research_keywords,
                'many_researched_foods': researched_foods,
            }


def get_relevant_substitutes(categories_id: list, nutriscore: str):
    """
    Returns the more relevant (with maximum of identical categories) substitutes list for the researched food
    according to its categories_id and nutriscore :
        1) if researched food has 3 categories tags : they are tried together
            >>> if result is 3 substitutes or less, paired categories combinations are tried
                >>> if results are also 3 substitutes or less, singled categories are tried
                    >>> if results are still 3 substitutes or less, None is returned
        2) if researched food has 2 categories tags : they are tried together
            >>> if results are 3 substitutes or less, singled categories are tried
                >>> if results are still 3 substitutes or less, None is returned
        3) if researched food has only 1 category tag : it is tried
            >>> if result is 3 substitutes or less, None is returned
    """
    nb_categories = len(categories_id)
    # See docstring 1)
    if nb_categories == 3:
        substitutes = several_categories_query(categories_id, nutriscore)
        if len(substitutes) > 3:
            return substitutes
        else:
            substitutes_for_paired_categories_combinations = []
            for pair in itert.combinations(categories_id, 2):
                substitutes_for_paired_categories_combinations.append(several_categories_query(pair, nutriscore))
            substitutes = longest_substitutes_list(substitutes_for_paired_categories_combinations)
            if len(substitutes) > 3:
                return substitutes
            else:
                substitutes = longest_substitutes_list(singled_categories_queries(categories_id, nutriscore))
                return substitutes if len(substitutes) > 3 else None
    # See docstring 2)
    elif nb_categories == 2:
        substitutes = several_categories_query(categories_id, nutriscore)
        if len(substitutes) > 3:
            return substitutes
        else:
            substitutes = longest_substitutes_list(singled_categories_queries(categories_id, nutriscore))
            return substitutes if len(substitutes) > 3 else None
    # See docstring 3)
    elif nb_categories == 1:
        substitutes = Food.objects.filter(category__id=categories_id[0]).filter(nutri_score__lt=nutriscore)
        return substitutes if len(substitutes) > 3 else None


def several_categories_query(categories_id: list, nutriscore: str):
    substitutes = Food.objects.filter(category__id=categories_id[0])
    for id in itert.islice(categories_id, 1, None):
        substitutes = substitutes.filter(category__id=id)
    return substitutes.filter(nutri_score__lt=nutriscore)


def singled_categories_queries(categories_id: list, nutriscore: str):
    substitutes_for_singled_categories = []
    for cat in categories_id:
        substitutes_for_singled_categories.append(Food.objects.filter(category__id=cat)
                                                              .filter(nutri_score__lt=nutriscore))
    return substitutes_for_singled_categories


def longest_substitutes_list(substitutes_lists: list) -> list:
    best_pair = max((len(i) for i in substitutes_lists))
    for substitutes in substitutes_lists:
        if len(substitutes) == best_pair:
            return substitutes


def add_food_categories(food: Food):
    if isinstance(food, Food):
        food.categories = list(food.category_set.all())
    elif isinstance(food, QuerySet):
        for f in food:
            f.categories = list(f.category_set.all())
    return food