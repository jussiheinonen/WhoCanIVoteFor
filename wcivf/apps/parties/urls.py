from django.urls import re_path

from .views import PartiesView, PartyView

urlpatterns = [
    re_path(r"^$", PartiesView.as_view(), name="parties_view"),
    re_path(
        r"^(?P<pk>[^/]+)/(?P<ignored_slug>.*)$",
        PartyView.as_view(),
        name="party_view",
    ),
]
