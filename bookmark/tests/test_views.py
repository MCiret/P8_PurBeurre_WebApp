from django.test import TestCase, TransactionTestCase
from django.urls import reverse
import filldb_tests_module.crud_functions_to_test as crud


class BookmarkViewsTests(TestCase):

    def test_bookmark_view(self):
        # Test for user with no bookmarks
        crud.create_user("user_test@gmail.com", "titi6789")
        self.client.login(username="user_test@gmail.com", password="titi6789")
        response_user_logged = self.client.get(reverse('bookmark:bookmark-page'))
        self.assertContains(response_user_logged, "Vos aliments substituts sauvegardés", status_code=200)
        self.assertContains(response_user_logged, "Vous n'avez aucun aliment substitut sauvegardé...", status_code=200)

        # Test for user with bookmarks
        crud.create_food("1", "b", "food1")
        crud.create_food("2", "d", "food2")
        crud.create_bookmark("user_test@gmail.com", "1")
        crud.create_bookmark("user_test@gmail.com", "2")
        response_user_logged2 = self.client.get(reverse('bookmark:bookmark-page'))
        self.assertContains(response_user_logged2, "Vos aliments substituts sauvegardés", status_code=200)
        self.assertNotContains(response_user_logged2, "Vous n'avez aucun aliment substitut sauvegardé...",
                               status_code=200)
        self.assertContains(response_user_logged2, "food1")
        self.assertContains(response_user_logged2, "food2")


class BookmarkViewsTestsWithTransaction(TransactionTestCase):

    def test_add_bookmark_view(self):
        crud.create_user("user_test@gmail.com", "titi6789")
        self.client.login(username="user_test@gmail.com", password="titi6789")
        # Create mock foods with 3 shared categories in test database
        crud.create_food("1", "c", "food1")
        crud.create_food("2", "d", "food2")
        crud.create_food("3", "a", "food3")
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

        response = self.client.get(reverse('bookmark:bookmark-add', kwargs={'selected_food': 1}),
                                   {'bookmark_food_barcode': 3}, follow=True)
        self.assertContains(response, "food1", status_code=200)
        self.assertContains(response, "food3", status_code=200)
        self.assertContains(response, "Sauvegardé", status_code=200)
        self.assertNotContains(response, "Sauvegarder", status_code=200)
