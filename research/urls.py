from django.urls import path
from research.views import HomePageView, ResultView, FoodView

app_name = 'research'

urlpatterns = [
    path('', HomePageView.as_view(), name="home-page"),
    path('result/', ResultView.as_view(), name="form-page"),
    path('result/<int:selected_food>', ResultView.as_view(), name="result-page"),
    path('food/<int:pk>', FoodView.as_view(), name="food-page"),
]
