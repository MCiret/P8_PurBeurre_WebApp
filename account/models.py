from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    # To have a unique email field in DB...
    email = models.EmailField("user email", unique=True)
    username = models.CharField(null=True, max_length=25)
    # ... to use the email as user's identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('',)

    def get_absolute_url(self):
        return reverse('account:user-create')
