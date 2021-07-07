from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
# from django.conf import settings


class UserCreateForm(auth_forms.UserCreationForm):

    class Meta(auth_forms.UserCreationForm.Meta):
        model = get_user_model()
        fields = ('email',)

class UserModifyForm(auth_forms.UserChangeForm):

    class Meta(auth_forms.UserChangeForm.Meta):
        model = get_user_model()
