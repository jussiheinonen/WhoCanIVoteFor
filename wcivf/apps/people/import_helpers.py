import sys
from django.conf import settings
from django.utils.http import urlencode

from wcivf.apps.elections.helpers import JsonPaginator


class YNRRecentPersonImporter:
    def __init__(self, base_url=None, params=None):
        self.base_url = base_url or f"{settings.YNR_BASE}/api/next/people"
        self.params = {"page_size": 200}
        if params:
            self.params.update(params)

    @property
    def import_url(self):
        querysting = urlencode(self.params)
        return f"{self.base_url}/?{querysting}"

    @property
    def people_to_import(self):
        for page in self.paginator(url=self.import_url):
            yield page

    def paginator(self, url):
        return JsonPaginator(page1=url, stdout=sys.stdout)
