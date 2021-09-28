from django.urls import include, re_path
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
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
        re_path(r"^admin/", admin.site.urls),
        re_path(r"^", include("core.urls")),
        re_path(r"^elections/", include("elections.urls")),
        re_path(r"^results/", include("results.urls")),
        re_path(r"^parties/", include("parties.urls")),
        re_path(r"^person/", include("people.urls")),
        re_path(r"^feedback/", include("feedback.urls")),
        re_path(r"^api/", include(("api.urls", "api"), namespace="api")),
        re_path(
            r"^sitemap\.xml$",
            cache_page(86400)(sitemap),
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        re_path(r"^robots\.txt", include("robots.urls")),
        re_path(
            r"^mailing_list/", include("mailing_list.urls", "dc_signup_form")
        ),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)


if settings.DEBUG:
    import debug_toolbar
    from dc_utils.urls import dc_utils_testing_patterns

    urlpatterns = (
        [re_path(r"^__debug__/", include(debug_toolbar.urls))]
        + dc_utils_testing_patterns
        + urlpatterns
    )
