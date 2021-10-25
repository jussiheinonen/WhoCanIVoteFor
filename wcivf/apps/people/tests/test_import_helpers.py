from django.conf import settings
from people.import_helpers import YNRPersonImporter
from elections.helpers import JsonPaginator


class TestYNRPersonImporter:
    def test_importer_init(self):
        importer = YNRPersonImporter(
            base_url="http://example.com", params={"foo": "bar"}
        )
        assert importer.params == {"foo": "bar", "page_size": 200}
        assert importer.base_url == "http://example.com"

    def test_import_url(self):
        params = {"foo": "bar"}
        importer = YNRPersonImporter(params=params)
        expected = f"{settings.YNR_BASE}/api/next/people/?page_size=200&foo=bar"
        assert importer.import_url == expected

    def test_paginator(self):
        importer = YNRPersonImporter()
        assert type(importer.paginator(url="foobar")) is JsonPaginator

    def test_people_to_import(self, mocker):
        importer = YNRPersonImporter()
        mocker.patch.object(importer, "paginator", return_value=[])
        result = importer.people_to_import

        assert list(result) == []
        importer.paginator.assert_called_once_with(url=importer.import_url)
