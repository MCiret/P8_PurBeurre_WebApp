from django.urls import path

from account.views import UserCreateView, UserLoginView, UserAccountView, UserLogoutView

app_name = 'account'

urlpatterns = [
    path('accounts/create/', UserCreateView.as_view(), name="user-create"),
    path('accounts/login/', UserLoginView.as_view(), name="user-login"),
    path('accounts/account/', UserAccountView.as_view(), name="user-account"),
    path('accounts/logout/', UserLogoutView.as_view(), name="user-logout"),
]
