from django.urls import re_path

from .views import ResultsListView

urlpatterns = [
    re_path(r"^$", ResultsListView.as_view(), name="results_list_view")
]
