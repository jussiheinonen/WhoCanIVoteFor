from django.urls import re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from .views import HomePageView, StatusCheckView, OpenSearchView

urlpatterns = [
    re_path(r"^$", HomePageView.as_view(), name="home_view"),
    re_path(
        r"^privacy/$",
        RedirectView.as_view(
            url="https://democracyclub.org.uk/privacy/", permanent=True
        ),
        name="privacy_view",
    ),
    re_path(
        r"^about/$",
        TemplateView.as_view(template_name="about.html"),
        name="about_view",
    ),
    re_path(
        r"^standing/$",
        TemplateView.as_view(template_name="standing.html"),
        name="standing_as_a_candidate",
    ),
    re_path(
        r"^_status_check/$", StatusCheckView.as_view(), name="status_check_view"
    ),
    re_path(r"^opensearch\.xml", OpenSearchView.as_view(), name="opensearch"),
]
