from django.test import TestCase, TransactionTestCase
from unittest import mock
import research.substitutes_research as subr
import filldb_tests_module.crud_func_for_testing as crud
from research.models import Food, Category


class SubstitutesResearchTestsExceptSQL(TestCase):
    """ Tests functions except db queries parts which are mocked """

    @mock.patch('research.models.Food.objects.filter')
    def test_look_for_substitutes_find_enough_substitutes(self, mock_filter):
        mock_filter.return_value = [1, 1, 1, 1, 1]

        self.assertEqual(subr.look_for_substitutes(["c1", "c2", "c3"], "nutriscore"), [1, 1, 1, 1, 1])
        self.assertTrue(mock_filter.called)
        self.assertEqual(mock_filter.call_args.kwargs['category__id'], "c1")

    @mock.patch('research.models.Food.objects.filter')
    def test_look_for_substitutes_find_none_substitute(self, mock_filter):
        mock_filter.return_value = []

        self.assertEqual(subr.look_for_substitutes(["c1", "c2", "c3", "c4", "c5", "c6"], "nutriscore"), None)
        self.assertTrue(mock_filter.called)
        self.assertEqual(mock_filter.call_count, 4)

    @mock.patch('django.db.models.QuerySet.filter')
    def test_look_for_foods_matching_user_research_according_to_db_query_result(self, mock_filter):
        # if user research keywords matches with several foods in db
        mock_filter.return_value = [1, 1, 1, 1, 1]
        result = {
            "valid": None,
            "error": None,
            "data": {
                "search_keywords": "",
                "perfect_match": None,
                "substitutes_foods": None
            }
        }
        subr.look_for_foods_matching_user_search("keywords", result)
        self.assertEqual(result["data"]["search_keywords"], "")
        self.assertTrue(result["valid"])
        self.assertEqual(result["data"]["several_matches"], [1, 1, 1, 1, 1])

        # if db empty
        result = {
            "valid": None,
            "error": None,
            "data": {
                "search_keywords": "",
                "perfect_match" : None,
                "substitutes_foods": None
            }
        }
        mock_filter.return_value = []
        subr.look_for_foods_matching_user_search("keywords", result)
        self.assertEqual(result["data"]["search_keywords"], "")
        self.assertIsNone(result["data"].get("several_matches", None))
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Empty DB")

        # if user research keywords matches exactly 1 food in db
        result = {
            "valid": None,
            "error": None,
            "data": {
                "search_keywords": "",
                "perfect_match" : None,
                "substitutes_foods": None
            }
        }
        mock_filter.return_value = [1]
        subr.look_for_foods_matching_user_search("keywords", result)
        self.assertEqual(result["data"]["search_keywords"], "")
        self.assertTrue(result["valid"])
        self.assertEqual(result["data"]["perfect_match"], 1)


class SubstitutesResearchTestsOnlySQL(TransactionTestCase):
    """ Tests only db queries """

    def setUp(self):
        """ Called to fill the test database for each following test method """
        # The food to be used as the researched food :
        crud.create_food("1", "c", "food1")
        crud.create_category(food_barcode="1", category_name="c1", category_rank="1")
        crud.create_category(food_barcode="1", category_name="c2", category_rank="2")
        crud.create_category(food_barcode="1", category_name="c3", category_rank="3")
        # The substitute which should be returned for the researched food :
        crud.create_food("2", "b", "food2")
        crud.create_category(food_barcode="2", category_name="c1", category_rank="1")
        crud.create_category(food_barcode="2", category_name="c2", category_rank="2")
        crud.create_category(food_barcode="2", category_name="c4", category_rank="3")
        # Not a substitute for the researched food because of nutriscore :
        crud.create_food("3", "c", "food3")
        crud.create_category(food_barcode="3", category_name="c1", category_rank="1")
        crud.create_category(food_barcode="3", category_name="c2", category_rank="2")
        crud.create_category(food_barcode="3", category_name="c3", category_rank="3")
        # Not a substitute for the researched food because of categories :
        crud.create_food("4", "a", "food4")
        crud.create_category(food_barcode="4", category_name="c4", category_rank="1")
        crud.create_category(food_barcode="4", category_name="c5", category_rank="2")
        crud.create_category(food_barcode="4", category_name="c6", category_rank="3")

    def test_sql_in_look_for_substitutes_function(self):
        # Get categories id for the researched food
        food_categories_id = [Category.objects.get(name='c1').id,
                              Category.objects.get(name='c2').id,
                              Category.objects.get(name='c3').id]

        self.assertQuerysetEqual(subr.look_for_substitutes(food_categories_id, "c"),
                                                          (Food.objects.filter(barcode="2")), ordered=False)

    def test_sql_in_look_for_foods_matching_user_research_function(self):
        result = {
            "valid": None,
            "error": None,
            "data": {
                "search_keywords": "",
                "perfect_match" : None,
                "substitutes_foods": None
            }
        }
        # With "food" research keyword, all foods in db should be returned :
        subr.look_for_foods_matching_user_search("food", result)
        self.assertQuerysetEqual(result["data"]['several_matches'],
                                 Food.objects.all(), ordered=False)
        # With "d3" research keyword :
        result = {
            "valid": None,
            "error": None,
            "data": {
                "search_keywords": "",
                "perfect_match" : None,
                "substitutes_foods": None
            }
        }
        subr.look_for_foods_matching_user_search("d3", result)
        self.assertEqual(result["data"]['perfect_match'],
                         Food.objects.get(barcode="3"))

    @mock.patch('research.substitutes_research.look_for_substitutes')
    def test_sql_of_research_in_db(self, mock_look_sub):
        mock_look_sub.return_value = "substitutes"

        # If called with the research_keywords argument, only 1 test to do :
        # categories that will be used for look_for_substitutes() are well ranked.
        subr.db_food_search(search_keywords="d3")
        ranked_categories_ids = [Category.objects.get(name="c1").id,
                                 Category.objects.get(name="c2").id,
                                 Category.objects.get(name="c3").id]
        self.assertEqual(mock_look_sub.call_args.args[0], ranked_categories_ids)

        # If called with the food_barcode argument, 2 tests to do :
        # 1) the Food.objects.get() returned the good researched food,
        # 2) the same as above.
        self.assertEqual(subr.db_food_search(food_barcode="3")["data"]["perfect_match"],
                         Food.objects.get(barcode=3))
        ranked_categories_ids = [Category.objects.get(name="c1").id,
                                 Category.objects.get(name="c2").id,
                                 Category.objects.get(name="c3").id]
        self.assertEqual(mock_look_sub.call_args.args[0], ranked_categories_ids)