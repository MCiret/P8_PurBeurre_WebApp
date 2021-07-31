from account.models import User
from research.models import Food
from django.db.utils import IntegrityError


def get_user_bookmarks(user_email: str):
    user = User.objects.get(email=user_email)
    return user.bookmarks.all()


def save_bookmark(user_email: str, substitute_barcode: int):
    user = User.objects.get(email=str(user_email))
    bookmark = Food.objects.get(barcode=substitute_barcode)
    try:
        user.bookmarks.add(bookmark)
    except IntegrityError:
        pass


def add_bookmarks_to_context(user_email: str):
    return [barcode['barcode'] for barcode in get_user_bookmarks(user_email).values('barcode')]