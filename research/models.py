from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=150)
    nutri_score = models.CharField(max_length=1)
    image_url = models.TextField()
    nutriment_url = models.TextField()
    off_url = models.TextField()
    category = models.CharField(max_length=150)
