import sys
from django.conf import settings
from django.utils.http import urlencode

from elections.helpers import JsonPaginator


class YNRPersonImporter:
    def __init__(self, base_url=None, params=None, stdout=None):
        self.base_url = base_url or settings.YNR_BASE
        self.params = {"page_size": 200}
        self.stdout = stdout or sys.stdout
        if params:
            self.params.update(params)

    @property
    def import_url(self):
        querystring = urlencode(self.params)
        return f"{self.base_url}/api/next/people/?{querystring}"

    @property
    def people_to_import(self):
        for page in self.paginator(url=self.import_url):
            yield page

    def paginator(self, url):
        return JsonPaginator(page1=url, stdout=self.stdout)
