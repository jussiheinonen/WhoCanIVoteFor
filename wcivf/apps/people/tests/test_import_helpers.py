from django.conf import settings
from django.db.models import QuerySet

from people.import_helpers import YNRPersonImporter
from elections.helpers import JsonPaginator
from people.models import Person


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

    def test_deleted_people_url(self):
        params = {
            "created": "2021-10-26",
            "action_type": "person-delete",
        }
        importer = YNRPersonImporter(params=params)

        expected = f"{settings.YNR_BASE}/api/next/logged_actions/?page_size=200&created=2021-10-26&action_type=person-delete"
        assert importer.deleted_people_url == expected

    def test_deleted_people(self, mocker):
        importer = YNRPersonImporter()
        mocker.patch.object(
            importer,
            "paginator",
            return_value=[{"results": ["list", "of", "objects"]}],
        )
        result = importer.deleted_people

        assert list(result) == ["list", "of", "objects"]
        importer.paginator.assert_called_once_with(
            url=importer.deleted_people_url
        )

    def test_delete_deleted_people(self, mocker):
        mocker.patch.object(
            YNRPersonImporter,
            "deleted_people",
            new_callable=mocker.PropertyMock,
            return_value=[
                {"unused": "data", "person_pk": 1},
                {"unused": "data", "person_pk": 2},
                {"unused": "data", "person_pk": 3},
            ],
        )
        mock_qs = mocker.MagicMock(spec=QuerySet)
        mock_qs.delete.return_value = 0, {}
        mocker.patch.object(Person.objects, "filter", return_value=mock_qs)

        importer = YNRPersonImporter()
        importer.delete_deleted_people()

        Person.objects.filter.assert_called_once_with(ynr_id__in=[1, 2, 3])
        mock_qs.delete.assert_called_once()
