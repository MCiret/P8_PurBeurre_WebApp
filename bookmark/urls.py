from django.urls import path
from bookmark.views import BookmarkView, AddBookmarkView

app_name = 'bookmark'

urlpatterns = [
    path('bookmark/', BookmarkView.as_view(), name="bookmark-page"),
    path('bookmark/<int:selected_food>', AddBookmarkView.as_view(), name="bookmark-add"),
]
