from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index
from django.views.decorators.cache import cache_page

from elections.sitemaps import ElectionSitemap, PostElectionSitemap
from people.sitemaps import PersonSitemap
from parties.sitemaps import PartySitemap

sitemaps = {
    "elections": ElectionSitemap,
    "postelections": PostElectionSitemap,
    "people": PersonSitemap,
    "parties": PartySitemap,
}

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", include("core.urls")),
        path("elections/", include("elections.urls")),
        path("parties/", include("parties.urls")),
        path("person/", include("people.urls")),
        path("feedback/", include("feedback.urls")),
        path("api/", include(("api.urls", "api"), namespace="api")),
        path(
            "sitemap.xml",
            cache_page(86400)(index),
            {"sitemaps": sitemaps},
        ),
        path(
            "sitemap-<section>.xml",
            cache_page(86400)(sitemap),
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path("robots.txt", include("robots.urls")),
        path("mailing_list/", include("mailing_list.urls", "dc_signup_form")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)


if settings.DEBUG:
    import debug_toolbar
    from dc_utils.urls import dc_utils_testing_patterns

    urlpatterns = (
        [path("__debug__/", include(debug_toolbar.urls))]
        + dc_utils_testing_patterns
        + urlpatterns
    )
