from django.db import models

class Food(models.Model):
    barcode = models.CharField(primary_key=True, max_length=30)
    category = models.CharField(max_length=150)
    image_url = models.TextField()
    nutriment_url = models.TextField()
    nutri_score = models.CharField(max_length=1)
    name = models.CharField(max_length=150)
    off_url = models.TextField()