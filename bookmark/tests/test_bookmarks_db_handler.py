from django.test import TestCase
from unittest import mock
import crud_functions_to_test as crud
import bookmark.bookmarks_db_handler as bdh
from account.models import User
from research.models import Food


class BookmarksDBHandler(TestCase):

    def setUp(self):
        crud.create_food("1", "b", "food1")
        crud.create_food("2", "d", "food2")
        crud.create_food("3", "c", "food3")
        crud.create_food("4", "e", "food4")
        crud.create_user("user1@mail.fr", "passuser1")
        crud.create_bookmark("user1@mail.fr", "1")
        crud.create_bookmark("user1@mail.fr", "2")

    def test_get_user_bookmarks(self):
        user = User.objects.get(email="user1@mail.fr")
        self.assertQuerysetEqual(user.bookmarks.all(), bdh.get_user_bookmarks("user1@mail.fr"), ordered=False)

    def test_save_bookmark(self):
        bdh.save_bookmark("user1@mail.fr", "3")
        user = User.objects.get(email="user1@mail.fr")
        self.assertIn(Food.objects.get(barcode="3"), user.bookmarks.all())

    @mock.patch('bookmark.bookmarks_db_handler.get_user_bookmarks')
    def test_add_bookmarks_to_context(self, mock_get):
        user = User.objects.get(email="user1@mail.fr")
        mock_get.return_value = user.bookmarks.all()

        self.assertIn("1", bdh.add_bookmarks_to_context("user1@mail.fr"))
        self.assertIn("2", bdh.add_bookmarks_to_context("user1@mail.fr"))
        self.assertNotIn("3", bdh.add_bookmarks_to_context("user1@mail.fr"))
        self.assertNotIn("4", bdh.add_bookmarks_to_context("user1@mail.fr"))
        self.assertNotIn("5", bdh.add_bookmarks_to_context("user1@mail.fr"))
