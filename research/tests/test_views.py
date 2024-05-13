from django.test import TestCase, TransactionTestCase
from django.urls import reverse
import filldb_tests_module.crud_func_for_testing as crud
from research.models import Food


class ResearchViewsTests(TestCase):

    def test_home_view(self):
        # test with unlogged user :
        response_no_user_logged = self.client.get(reverse('research:home-page'))
        self.assertContains(response_no_user_logged, "Du gras, oui, mais de qualité !", status_code=200)
        self.assertNotContains(response_no_user_logged, "href=/accounts/logout")
        self.assertContains(response_no_user_logged, "href=/accounts/create/")

        # test with logged user :
        crud.create_user("user_test", "titi6789")
        self.client.login(username="user_test", password="titi6789")
        response_user_logged = self.client.get(reverse('research:home-page'))
        self.assertContains(response_user_logged, "Du gras, oui, mais de qualité !", status_code=200)
        self.assertContains(response_user_logged, "accounts/logout")
        self.assertNotContains(response_user_logged, "accounts/create")

    def test_result_view_if_researched_food_not_in_db(self):
        crud.create_food("1", "c", "food1")
        response = self.client.get(reverse('research:form-page'), {'research': "absent food"})
        self.assertTrue(response.context["valid"])
        self.assertIsNone(response.context["data"]["perfect_match"])
        self.assertEqual(response.context["data"]["search_keywords"], 'absent food')
        self.assertContains(response, "Aucun aliment ne correspond à votre recherche...", status_code=200)

    def test_result_view_if_researched_food_is_in_db_and_match_one_food(self):
        mock_food = crud.create_food("1", "c", "food1")

        response = self.client.get(reverse('research:form-page'), {'research': "od1"})
        self.assertIsNotNone(response.context["data"]["perfect_match"])
        self.assertEqual(response.context["data"]["perfect_match"], mock_food)
        self.assertContains(response, mock_food.name, status_code=200)

    def test_result_view_if_researched_food_in_db_and_match_many_foods(self):
        # Create mock foods in test database
        mock_food1 = crud.create_food("1", "c", "food1")
        mock_food2 = crud.create_food("2", "d", "food2")
        mock_food3 = crud.create_food("3", "a", "food3")

        # If user's research keywords corresponds to many foods in database, 2 tests to do :
        # 1) Test of view returning several foods to be chosen by user
        response = self.client.get(reverse('research:form-page'), {'research': "od"})
        self.assertIsNone(response.context["data"]["perfect_match"])
        self.assertIsNotNone(response.context["data"]["several_matches"])
        self.assertEqual(list(response.context["data"]["several_matches"]),
                         [mock_food1, mock_food2, mock_food3])
        self.assertQuerysetEqual(response.context["data"]["several_matches"], Food.objects.all(), ordered=False)
        self.assertContains(response, "Plusieurs aliments correspondent à votre recherche...", status_code=200)

        # 2) Test of returning the result view when user has chosen one food
        response2 = self.client.get(reverse('research:result-page',  kwargs={'selected_food': 1}))
        self.assertIsNotNone(response2.context["data"]["perfect_match"])
        self.assertEqual(response2.context["data"]["perfect_match"], mock_food1)

    def test_food_view(self):
        crud.create_food("1", "c", "food1")
        response = self.client.get(reverse('research:food-page', kwargs={'pk': 1}))
        self.assertContains(response, "food1", status_code=200)


class ResearchViewsTestsWithTransaction(TransactionTestCase):

    def test_result_view_if_substitutes_are_found(self):
        # Create mock foods with 3 shared categories in test database
        mock_food1 = crud.create_food("1", "c", "food1")
        crud.create_food("2", "d", "food2")
        mock_food3 = crud.create_food("3", "a", "food3")
        # At least 3 categories because of look_for_substitutes() in research/substitutes_research.py
        crud.create_category("1", "c1", "1")
        crud.create_category("2", "c1", "1")
        crud.create_category("3", "c1", "1")
        crud.create_category("1", "c2", "2")
        crud.create_category("2", "c2", "2")
        crud.create_category("3", "c2", "2")
        crud.create_category("1", "c3", "3")
        crud.create_category("2", "c3", "3")
        crud.create_category("3", "c3", "3")

        # test with unlogged user :
        response_no_user_logged = self.client.get(reverse('research:form-page'), {'research': "od1"})
        self.assertIsNotNone(response_no_user_logged.context["data"]["perfect_match"])
        self.assertEqual(response_no_user_logged.context["data"]["perfect_match"], mock_food1)
        self.assertContains(response_no_user_logged, mock_food1.name, status_code=200)
        self.assertEqual(response_no_user_logged.context["data"]['substitutes_foods'].get(), mock_food3)
        self.assertNotContains(response_no_user_logged, "Sauvegard", status_code=200)

        # test with logged user :
        crud.create_user("user_test", "titi6789")
        self.client.login(username="user_test", password="titi6789")
        response_user_logged = self.client.get(reverse('research:form-page'), {'research': "od1"})
        self.assertIsNotNone(response_user_logged.context["data"]["perfect_match"])
        self.assertEqual(response_user_logged.context["data"]["perfect_match"], mock_food1)
        self.assertContains(response_user_logged, mock_food1.name, status_code=200)
        self.assertEqual(response_user_logged.context["data"]['substitutes_foods'].get(), mock_food3)
        self.assertContains(response_user_logged, "Sauvegard", status_code=200)
