from django.urls import path

from account.views import UserCreateView

app_name = 'account'

urlpatterns = [
    path('account/', UserCreateView.as_view(), name="user-create"),
]