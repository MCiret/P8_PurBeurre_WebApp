from django.test import TestCase
from unittest import mock
from django.urls import reverse
import filldb_tests_module.crud_func_for_testing as crud
from account.models import User
from account.views import UserAccountView


class AccountViewsTests(TestCase):

    def test_user_create_view(self):
        # Test empty user creation form displaying :
        response_get = self.client.get(reverse('account:user-create'))
        self.assertContains(response_get, "Créer le compte", status_code=200)
        self.assertContains(response_get, "Si vous avez déjà un compte Pur Beurre :", status_code=200)

        # Test successful user creation in db using the form :
        response_post = self.client.post(reverse('account:user-create'), {
                                         'email': 'user_test@mail.com',
                                         'password1': 'toto1598',
                                         'password2': 'toto1598'}, follow=True)

        # Test home page redirect when form is validated :
        self.assertContains(response_post, "Du gras, oui, mais de qualité !", status_code=200)

        # Test user is in db :
        self.assertEqual(User.objects.get().email, 'user_test@mail.com')

        # Test failing user creation in db using the form :
        response_post2 = self.client.post(reverse('account:user-create'), {
                                         'email': 'user_test@mail.com',
                                         'password1': 'toto1598',
                                         'password2': 'toto159'})
        # Test user create page is redisplayed if form is not validated :
        self.assertContains(response_post2, "Créer le compte", status_code=200)
        self.assertContains(response_post2, "Si vous avez déjà un compte Pur Beurre :", status_code=200)

    def test_user_login_view(self):
        # Test empty user login form displaying :
        response_get = self.client.get(reverse('account:user-login'))
        self.assertContains(response_get, "Se connecter", status_code=200)

        # Test successful user login :
        crud.create_user('user_test@mail.com', 'tutu3574')
        response_post = self.client.post(reverse('account:user-login'), {
                                         'username': 'user_test@mail.com',
                                         'password': 'tutu3574', 'next': '/'}, follow=True)
        # the 'next' value is set in the form (see hidden input in the html template)
        # and not in the view so it has to be passed with post params
        # (like the username and password field values)

        # Test home page redirect when form is validated and user is logged :
        self.assertContains(response_post, "Du gras, oui, mais de qualité !", status_code=200)

        # Test failing user login :
        response_post2 = self.client.post(reverse('account:user-login'), {
                                          'username': 'user_test@mail.com',
                                          'password': 'tutu357'})
        # Test user login page is redisplayed if form is not validated :
        self.assertContains(response_post2, "Se connecter", status_code=200)

    def test_extract_user_name_from_mail(self):
        self.assertEqual(UserAccountView.extract_user_name_from_mail("abcde@mail.fr"), "abcde")

    @mock.patch('account.views.UserAccountView.extract_user_name_from_mail')
    def test_user_account_view(self, mock_extract):

        mock_extract.return_value = "user_test"

        crud.create_user("user_test@gmail.com", "titi6789")
        self.client.login(username="user_test@gmail.com", password="titi6789")

        response_user_logged = self.client.get(reverse('account:user-account'))

        self.assertTrue(mock_extract.called)
        self.assertContains(response_user_logged, "user_test !", status_code=200)
        self.assertContains(response_user_logged, "user_test@gmail.com", status_code=200)

    def test_user_logout_view(self):
        crud.create_user("user_test@gmail.com", "titi6789")
        self.client.login(username="user_test@gmail.com", password="titi6789")

        response_user_logged = self.client.post(reverse('account:user-logout'), follow=True)

        self.assertContains(response_user_logged, "Du gras, oui, mais de qualité !", status_code=200)
