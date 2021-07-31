from account.forms import UserCreateForm
from account.models import User
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class UserCreateView(CreateView):
    model = User
    template_name = 'account/create-account.html'
    form_class = UserCreateForm


class UserLoginView(LoginView):
    template_name = 'account/login-account.html'


class UserAccountView(TemplateView):
    template_name = 'account/user-account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_name'] = UserAccountView.extract_user_name_from_mail(str(self.request.user))
        context['user_mail'] = self.request.user
        return context

    @staticmethod
    def extract_user_name_from_mail(mail: str):
        return mail[:mail.find('@')]


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('research:home-page')
    # class attributes are evaluated on import that's why we use reverse_lazy() instead of reverse()
