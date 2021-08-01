from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from research.models import Food


class User(AbstractUser):

    # To have a unique email field in DB...
    email = models.EmailField("Email", unique=True)
    username = models.CharField(null=True, max_length=25)
    # To use the email as user's identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('',)

    bookmarks = models.ManyToManyField(Food)

    def get_absolute_url(self):
        return reverse('research:home-page')
