from django.test import TestCase, TransactionTestCase
from django.db.utils import IntegrityError
from unittest import mock
import json
import research.substitutes_research as subr
from research.models import Food, Category


class SubstitutesResearchNoDBQueriesTests(TestCase):
    """ Tests functions except db queries parts which are mocked """

    @mock.patch('research.models.Food.objects.filter')
    def test_look_for_substitutes_find_enough_substitutes(self, mock_filter):
        mock_filter.return_value = [1, 1, 1, 1, 1]

        self.assertEqual(subr.look_for_substitutes(["c1", "c2", "c3"], "nutriscore"), [1, 1, 1, 1, 1])
        self.assertTrue(mock_filter.called)
        self.assertEqual(mock_filter.call_args.kwargs['category__id'], "c1")

    @mock.patch('research.models.Food.objects.filter')
    def test_look_for_substitutes_dont_find_enough_substitutes(self, mock_filter):
        mock_filter.return_value = [1, 1]

        self.assertEqual(subr.look_for_substitutes(["c1", "c2", "c3", "c4", "c5", "c6"], "nutriscore"), None)
        self.assertTrue(mock_filter.called)
        self.assertEqual(mock_filter.call_count, 4)

    @mock.patch('django.db.models.QuerySet.filter')
    def test_look_for_matching_user_research_according_to_db_query_result(self, mock_filter):
        # if keywords matches with several foods in db
        mock_filter.return_value = [1, 1, 1, 1, 1]
        self.assertEqual(subr.look_for_foods_matching_user_research("keywords"), {
                'research_keywords': "keywords",
                'many_researched_foods': [1, 1, 1, 1, 1],
            })
        # if keywords doesn't match any food in db
        mock_filter.return_value = []
        self.assertEqual(subr.look_for_foods_matching_user_research("keywords"), {
                'research_keywords': "keywords"
            })
        # if keywords matches exactly 1 food in db
        mock_filter.return_value = [1]
        self.assertEqual(subr.look_for_foods_matching_user_research("keywords"), {
                'the_researched_food': 1
            })

    @mock.patch('research.substitutes_research.look_for_substitutes')
    @mock.patch('django.db.models.QuerySet.filter')
    @mock.patch('research.substitutes_research.look_for_foods_matching_user_research')
    def test_researchs_in_db_with_research_keywords_arg(self, mock_look_food, mock_filter, mock_look_sub):
        mock_food = Food("123", "irul", "nurl", "nutriscore", "name", "offurl")
        mock_look_food.return_value = {'the_researched_food': mock_food}
        mock_look_sub.return_value = "substitutes"

        self.assertEqual(subr.researchs_in_db(research_keywords="keywords"),
                         {'the_researched_food': mock_food, 'substitutes_foods': "substitutes"})
        self.assertTrue(mock_look_food.called)
        self.assertTrue(mock_filter.called)
        self.assertTrue(mock_look_sub.called)

        mock_look_food.return_value = {'research_keywords': "keywords"}
        self.assertEqual(subr.researchs_in_db(research_keywords="keywords"),
                         {'research_keywords': "keywords"})

    @mock.patch('research.substitutes_research.look_for_substitutes')
    @mock.patch('django.db.models.QuerySet.filter')
    @mock.patch('research.models.Food.objects.get')
    def test_researchs_in_db_with_food_barcode_arg(self, mock_get, mock_filter, mock_look_sub):
        mock_food = Food("123", "irul", "nurl", "nutriscore", "name", "offurl")
        mock_get.return_value = mock_food
        mock_look_sub.return_value = "substitutes"

        self.assertEqual(subr.researchs_in_db(food_barcode="barcode"),
                         {'the_researched_food': mock_food, 'substitutes_foods': "substitutes"})
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_filter.called)
        self.assertTrue(mock_look_sub.called)


class SubstitutesResearchDBQueriesTests(TransactionTestCase):
    """ Tests db queries """
    def create_foods(self, foods_dicts: list):
        for food_dict in foods_dicts:
            food = Food(food_dict["_id"], *list(food_dict.values())[2:])
            food.save()
        # categories_tags are ranked from the most general to the most specific
            for i, category in enumerate(reversed(food_dict["categories_tags"])):
                tmp_cat = Category(name=category)
                try:  # try to create this category in db...
                    tmp_cat.save()
                except IntegrityError:  # ...if this category's name is already in db whereas it has to be unique
                    Category.objects.get(name=category).foods.add(food, through_defaults={'category_rank': i+1})
                else:  # ...else just make the many-to-many relation
                    tmp_cat.foods.add(food, through_defaults={'category_rank': i+1})

    def test_look_for_substitutes_db_query(self):
        # json file where IF food.barcode = 3 is researched food
        # SO foods with barcode = 2, 5, 6 and 7 are substitutes :
        with open("research/tests/mocks_data/mock_foods_dicts.json", "r", encoding="utf-8") as json_file:
            mock_foods_dicts = json.load(json_file)
        self.create_foods(mock_foods_dicts)
        researched_food = Food.objects.get(barcode="3")
        food_categories_id = []
        for category in researched_food.category_set.all().order_by('categoryfoods__category_rank'):
            food_categories_id.append(Category.objects.filter(name=category.name).values('id')[0]['id'])

        self.assertQuerysetEqual(subr.look_for_substitutes(food_categories_id, researched_food.nutri_score),
                                                          (Food.objects.filter(barcode="2") |
                                                           Food.objects.filter(barcode="5") |
                                                           Food.objects.filter(barcode="6") |
                                                           Food.objects.filter(barcode="7")), ordered=False)

    def test_look_for_foods_matching_user_research_db_query(self):
        with open("research/tests/mocks_data/mock_foods_dicts.json", "r", encoding="utf-8") as json_file:
            mock_foods_dicts = json.load(json_file)
        self.create_foods(mock_foods_dicts)

        self.assertQuerysetEqual(subr.look_for_foods_matching_user_research("food")['many_researched_foods'],
                                 Food.objects.all(), ordered=False)
        self.assertEqual(subr.look_for_foods_matching_user_research("d3")['the_researched_food'],
                         Food.objects.get(barcode="3"))

    @mock.patch('research.substitutes_research.look_for_substitutes')
    def test_research_in_db_db_query(self, mock_look):
        mock_look.return_value = "substitutes"

        with open("research/tests/mocks_data/mock_foods_dicts.json", "r", encoding="utf-8") as json_file:
            mock_foods_dicts = json.load(json_file)
        self.create_foods(mock_foods_dicts)

        self.assertEqual(subr.researchs_in_db(food_barcode="3"), {
            'the_researched_food': Food.objects.get(barcode="3"),
            'substitutes_foods': "substitutes"})
        categories_ids = [Category.objects.get(name="c3").id,
                          Category.objects.get(name="c2").id,
                          Category.objects.get(name="c1").id]
        self.assertEqual(mock_look.call_args.args[0], categories_ids)
