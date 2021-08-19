from django.db.utils import IntegrityError
from research.models import Food, Category
from account.models import User
from typing import Union


def create_food(barcode, nutriscore, name) -> Union[Food, bool]:
    food = Food(barcode=barcode,
                image_url="iurl",
                nutriment_url="nurl",
                nutri_score=nutriscore,
                name=name,
                off_url="offurl")
    try:
        food.save()
    except IntegrityError:
        return False

    return food


def create_food_from_dict(food_dict: dict) -> None:
    food = Food(barcode=food_dict["_id"],
                image_url=food_dict["image_front_url"],
                nutriment_url=food_dict["image_nutrition_small_url"],
                nutri_score=food_dict["nutriscore_grade"],
                name=food_dict["product_name"],
                off_url=food_dict["url"])
    try:
        food.save()
    except IntegrityError:
        pass


def create_category(food_barcode: str, category_name: str, category_rank: str) -> None:
    food = Food.objects.get(barcode=food_barcode)
    cat = Category(name=category_name)
    try:
        cat.save()
    except IntegrityError:
        Category.objects.get(name=category_name).foods.add(food, through_defaults={'category_rank': category_rank})
    else:
        cat.foods.add(food, through_defaults={'category_rank': category_rank})


def create_user(email: str, password: str) -> Union[User, bool]:
    user = User(email=email)
    user.set_password(password)
    try:
        user.save()
    except IntegrityError:
        return False
    return user


def create_bookmark(user_email: str, substitute_barcode: int) -> bool:
    user = User.objects.get(email=str(user_email))
    bookmark = Food.objects.get(barcode=substitute_barcode)
    try:
        user.bookmarks.add(bookmark)
    except IntegrityError:
        return False
    return True
