from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from .models import Election, PostElection


class ElectionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Election.objects.all()


class PostElectionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = "https"

    # Only include posts for general elections, since
    # otherwise the sitemap gets close to the Google limit.
    # of 50,000 URLs.
    def items(self):
        return PostElection.objects.filter(
            Q(election__election_type="parl")
            | Q(election__election_type="2010")
            | Q(election__election_type="2015")
        ).order_by("-election__election_date")
