from django.urls import re_path

from .views import PersonView, EmailPersonView

urlpatterns = [
    re_path(
        r"^(?P<pk>[^/]+)/email/(?P<ignored_slug>.*)$",
        EmailPersonView.as_view(),
        name="email_person_view",
    ),
    re_path(
        r"^(?P<pk>[^/]+)/(?P<ignored_slug>.*)$",
        PersonView.as_view(),
        name="person_view",
    ),
]
