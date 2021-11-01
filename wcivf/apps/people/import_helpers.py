import sys
from django.conf import settings
from django.utils.http import urlencode

from elections.helpers import JsonPaginator
from people.models import Person


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
    def deleted_people_url(self):
        querystring = urlencode(self.params)
        return f"{self.base_url}/api/next/logged_actions/?{querystring}"

    @property
    def deleted_people(self):
        for page in self.paginator(url=self.deleted_people_url):
            yield from page["results"]

    @property
    def people_to_import(self):
        for page in self.paginator(url=self.import_url):
            yield page

    def paginator(self, url):
        return JsonPaginator(page1=url, stdout=self.stdout)

    def delete_deleted_people(self):
        deleted_ynr_pks = []
        for result in self.deleted_people:
            deleted_ynr_pks.append(result["person_pk"])

        _, deleted_dict = Person.objects.filter(
            ynr_id__in=deleted_ynr_pks
        ).delete()
        count = deleted_dict.get("people.Person", 0)
        self.stdout.write(f"Deleted {count} people")
