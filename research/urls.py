from django.urls import path
from django.views.generic import TemplateView
from research.views import HomePageView, ResultView, FoodView

app_name = 'research'

urlpatterns = [
    path('', HomePageView.as_view(), name="home-page"),
    path('legal_notice/', TemplateView.as_view(template_name='legal_notice.html'), name="legal-page"),
    path('result/', ResultView.as_view(), name="form-page"),
    path('result/<int:selected_food>', ResultView.as_view(), name="result-page"),
    path('food/<int:pk>', FoodView.as_view(), name="food-page"),
]
