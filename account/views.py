from account.forms import UserCreateForm, UserModifyForm
from account.models import User
from django.views.generic import CreateView

class UserCreateView(CreateView):
    model = User
    template_name = 'account/account.html'
    form_class = UserCreateForm