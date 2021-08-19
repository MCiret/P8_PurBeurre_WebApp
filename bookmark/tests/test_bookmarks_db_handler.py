from django.test import TestCase
from unittest import mock
import filldb_tests_module.crud_functions_to_test as crud
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
    def test_list_user_bookmarks_barcodes(self, mock_get):

        user = User.objects.get(email="user1@mail.fr")
        mock_get.return_value = user.bookmarks.all()

        bookmarks_barcodes_list = bdh.list_user_bookmarks_barcodes("user1@mail.fr")

        self.assertIn("1", bookmarks_barcodes_list)
        self.assertIn("2", bookmarks_barcodes_list)
        self.assertNotIn("3", bookmarks_barcodes_list)
        self.assertNotIn("4", bookmarks_barcodes_list)
        self.assertNotIn("5", bookmarks_barcodes_list)
