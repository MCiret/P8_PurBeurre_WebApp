from django.urls import path, re_path
from research.views import HomePageView, ResultView

app_name = 'research'

urlpatterns = [
    path('', HomePageView.as_view(), name="home-page"),
    path('result/', ResultView.as_view(), name="form-page"),
    path('result/<int:selected_food>', ResultView.as_view(), name="result-page"),
    # re_path(r'^result/(?P<selected_food>)', ResultView.as_view(), name="result-page"),
]
