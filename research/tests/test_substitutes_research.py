from django.test import TestCase, TransactionTestCase
from unittest import mock
import research.substitutes_research as subr
import filldb_tests_module.crud_functions_to_test as crud
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
        self.assertEqual(subr.look_for_foods_matching_user_research("keywords"), {
                'research_keywords': "keywords",
                'many_researched_foods': [1, 1, 1, 1, 1],
            })
        # if user research keywords doesn't match any food in db
        mock_filter.return_value = []
        self.assertEqual(subr.look_for_foods_matching_user_research("keywords"), {
                'research_keywords': "keywords"
            })
        # if user research keywords matches exactly 1 food in db
        mock_filter.return_value = [1]
        self.assertEqual(subr.look_for_foods_matching_user_research("keywords"), {
                'the_researched_food': 1
            })

    @mock.patch('research.substitutes_research.look_for_substitutes')
    @mock.patch('django.db.models.QuerySet.filter')
    @mock.patch('research.substitutes_research.look_for_foods_matching_user_research')
    def test_researchs_in_db_called_with_the_research_keywords_argument(self, mock_look_food,
                                                                        mock_filter, mock_look_sub):
        # test if user research keywords matches one food in db
        mock_food = Food("123", "irul", "nurl", "nutriscore", "name", "offurl")
        mock_look_food.return_value = {'the_researched_food': mock_food}
        mock_look_sub.return_value = "substitutes"

        self.assertEqual(subr.researchs_in_db(research_keywords="keywords"),
                         {'the_researched_food': mock_food, 'substitutes_foods': "substitutes"})
        self.assertTrue(mock_look_food.called)
        self.assertTrue(mock_filter.called)
        self.assertTrue(mock_look_sub.called)

        # test if user research keywords don't matches any food in db
        mock_look_food.called = False
        mock_filter.called = False
        mock_look_sub.called = False
        mock_look_food.return_value = {'research_keywords': "keywords"}
        self.assertEqual(subr.researchs_in_db(research_keywords="keywords"),
                         {'research_keywords': "keywords"})
        self.assertTrue(mock_look_food.called)
        self.assertFalse(mock_filter.called)
        self.assertFalse(mock_look_sub.called)

    @mock.patch('research.substitutes_research.look_for_substitutes')
    @mock.patch('django.db.models.QuerySet.filter')
    @mock.patch('research.models.Food.objects.get')
    def test_researchs_in_db_called_with_the_food_barcode_argument(self, mock_get, mock_filter, mock_look_sub):
        mock_food = Food("123", "irul", "nurl", "nutriscore", "name", "offurl")
        mock_get.return_value = mock_food
        mock_look_sub.return_value = "substitutes"

        self.assertEqual(subr.researchs_in_db(food_barcode="barcode"),
                         {'the_researched_food': mock_food, 'substitutes_foods': "substitutes"})
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_filter.called)
        self.assertTrue(mock_look_sub.called)


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
        # With "food" research keyword, all foods in db should be returned :
        self.assertQuerysetEqual(subr.look_for_foods_matching_user_research("food")['many_researched_foods'],
                                 Food.objects.all(), ordered=False)
        # With "d3" research keyword :
        self.assertEqual(subr.look_for_foods_matching_user_research("d3")['the_researched_food'],
                         Food.objects.get(barcode="3"))

    @mock.patch('research.substitutes_research.look_for_substitutes')
    @mock.patch('research.substitutes_research.look_for_foods_matching_user_research')
    def test_sql_of_research_in_db(self, mock_look_food, mock_look_sub):
        mock_researched_food = Food.objects.get(barcode="3")
        mock_look_food.return_value = {"the_researched_food": mock_researched_food}
        mock_look_sub.return_value = "substitutes"

        # If called with the research_keywords argument, only 1 test to do :
        # categories that will be used for look_for_substitutes() are well ranked.
        subr.researchs_in_db(research_keywords="d3")
        ranked_categories_ids = [Category.objects.get(name="c1").id,
                                 Category.objects.get(name="c2").id,
                                 Category.objects.get(name="c3").id]
        self.assertEqual(mock_look_sub.call_args.args[0], ranked_categories_ids)

        # If called with the food_barcode argument, 2 tests to do :
        # 1) the Food.objects.get() returned the good researched food,
        # 2) the same as above.
        self.assertEqual(subr.researchs_in_db(food_barcode="3"),
                         {'the_researched_food': mock_researched_food,
                          'substitutes_foods': "substitutes"})
        ranked_categories_ids = [Category.objects.get(name="c1").id,
                                 Category.objects.get(name="c2").id,
                                 Category.objects.get(name="c3").id]
        self.assertEqual(mock_look_sub.call_args.args[0], ranked_categories_ids)
