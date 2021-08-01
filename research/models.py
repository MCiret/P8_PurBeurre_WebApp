from django.db import models


class Food(models.Model):
    barcode = models.CharField(primary_key=True, max_length=30)
    image_url = models.TextField()
    nutriment_url = models.TextField()
    nutri_score = models.CharField(max_length=1)
    name = models.CharField(max_length=150)
    off_url = models.TextField()

    def __str__(self):
        return f"Aliment --> {self.barcode} - {self.name} - {self.nutri_score} - {self.off_url}"


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    foods = models.ManyToManyField(Food, through="CategoryFoods")

    def __str__(self):
        return f"Catégorie --> {self.name}"


class CategoryFoods(models.Model):
    """
        A Food + A Category
        + food's category rank in the hierarchy (used for substitutes research algorithm).
        See research/management/commands/filldb.py --> save_foods_in_db() for more infos about this rank.
    """
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category_rank = models.IntegerField()
