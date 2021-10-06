from django.conf import settings
import pytest
import sys

from django.test import TestCase
from elections.tests.factories import (
    PostFactory,
    ElectionFactory,
)
from elections.helpers import (
    get_election_timetable,
    EEHelper,
    JsonPaginator,
)
from elections.import_helpers import YNRBallotImporter, YNRPostImporter
from elections.models import Election, PostElection, Post
from datetime import date
from elections.tests.factories import PostElectionFactory


class GetElectionTimetable(TestCase):
    def test_with_territory_code_eng(self):
        expected = get_election_timetable("local.2019-05-02", "ENG")

        assert expected.poll_date == date(2019, 5, 2)

    def test_with_territory_code_nir(self):
        expected = get_election_timetable("local.2019-05-02", "NIR")

        assert expected.poll_date == date(2019, 5, 2)

    def test_with_territory_code_unknown(self):
        expected = get_election_timetable("local.2019-05-02", "-")

        assert expected is None

    def test_with_territory_code_unambiguous_election_type(self):
        expected = get_election_timetable("nia.belfast-east.2017-03-02", "NIR")

        assert expected.poll_date == date(2017, 3, 2)

    def test_with_territory_code_malformed_id(self):
        expected = get_election_timetable("whoknows", "ENG")

        assert expected is None


class TestEEHelper:
    @pytest.fixture
    def ee_helper(self, settings):
        settings.EE_BASE = "https://elections.democracyclub.org.uk"
        return EEHelper()

    def test_base_elections_url(self, ee_helper):
        assert (
            ee_helper.base_elections_url
            == "https://elections.democracyclub.org.uk/api/elections/"
        )

    @pytest.mark.freeze_time("2021-02-20")
    def test_deleted_election_ids(self, ee_helper, mocker):
        """
        Check a generator object of ID's to be deleted is returned.
        Patchs the JsonPaginator so that no actual API call is made, and
        instead return mock data to match the structure of the API
        """
        mock_data = [
            {"results": [{"election_id": "foo_id"}, {"election_id": "bar_id"}]},
        ]
        paginator = mocker.MagicMock(spec=JsonPaginator)
        paginator.return_value.__iter__.return_value = iter(mock_data)
        mocker.patch("elections.helpers.JsonPaginator", new=paginator)

        result = ee_helper.deleted_election_ids

        assert result == ["foo_id", "bar_id"]
        paginator.assert_called_once_with(
            page1="https://elections.democracyclub.org.uk/api/elections/?deleted=1&poll_open_date__gte=2021-01-01",
            stdout=sys.stdout,
        )

    @pytest.mark.django_db
    def test_deleted_deleted_elections(self, ee_helper, mocker):
        """
        Patch the EEHelper to return a list of ID's to be deleted
        Patch the filter method on the Election QuerySet
        Assert that the correct kwargs are passed to the filter call
        Assert that delete is called on the return value
        """
        mocker.patch.object(
            EEHelper,
            "deleted_election_ids",
            new_callable=mocker.PropertyMock,
            return_value=["foo_id", "bar_id"],
        )
        election_filter = mocker.MagicMock()
        election_filter.return_value.delete.return_value = ("foo", "bar")
        mocker.patch.object(Election.objects, "filter", new=election_filter)

        postelection_filter = mocker.MagicMock()
        postelection_filter.return_value.delete.return_value = ("foo", "bar")
        mocker.patch.object(
            PostElection.objects, "filter", new=postelection_filter
        )

        ee_helper.delete_deleted_elections()

        election_filter.assert_called_once_with(slug__in=["foo_id", "bar_id"])
        election_filter.return_value.delete.assert_called_once()
        postelection_filter.assert_called_once_with(
            ballot_paper_id__in=["foo_id", "bar_id"]
        )
        postelection_filter.return_value.delete.assert_called_once()


class TestYNRBallotImporter:
    @pytest.fixture
    def importer(self, mocker):
        importer = YNRBallotImporter()
        mocker.patch.object(importer.ee_helper, "prewarm_cache")
        mocker.patch.object(
            importer, "get_paginator", return_value=[mocker.Mock()]
        )
        mocker.patch.object(importer, "add_ballots")
        mocker.patch.object(importer, "run_post_ballot_import_tasks")
        mocker.patch.object(importer, "delete_orphan_posts")
        return importer

    @pytest.mark.django_db
    def test_delete_orphan_posts(self):
        importer = YNRBallotImporter()
        election = ElectionFactory(name="Adur local election")
        self.post = PostFactory(label="Adur local election")
        self.post.elections.add(election)
        self.orphan_post = PostFactory(
            label="Adur local election", ynr_id="foo"
        )

        deleted_posts, _ = importer.delete_orphan_posts()
        query_set = Post.objects.all()
        assert deleted_posts == 1
        assert query_set.count() == 1
        assert self.post in query_set
        assert self.orphan_post not in query_set

    def test_do_import_no_params(self, importer):
        """
        When no params and not current_only this is a full import the
        ee cache should be used and post ballot tasks should be run
        """
        assert importer.current_only is False
        assert importer.force_metadata is False
        importer.do_import(params=None)
        importer.ee_helper.prewarm_cache.assert_called_once_with(current=True)

        expected_url = (
            f"{settings.YNR_BASE}/media/cached-api/latest/ballots-000001.json"
        )
        importer.get_paginator.assert_called_once_with(expected_url)
        importer.add_ballots.assert_called_once()
        importer.run_post_ballot_import_tasks.assert_called_once()
        importer.delete_orphan_posts.assert_called_once()

    def test_do_import_with_params(self, importer):
        """
        When no params this is a not a full import so the cache should
        not be used and post ballot tasks not run
        """
        assert importer.current_only is False
        importer.do_import(params={"election_date": "2021-05-06"})
        importer.ee_helper.prewarm_cache.assert_not_called()

        expected_url = f"{settings.YNR_BASE}/api/next/ballots/?page_size=200&election_date=2021-05-06"
        importer.get_paginator.assert_called_once_with(expected_url)
        importer.add_ballots.assert_called_once()
        importer.run_post_ballot_import_tasks.assert_not_called()
        importer.delete_orphan_posts.assert_called_once()

    def test_do_import_no_params_current_only(self, importer):
        """
        When no params this is a not a full import so the cache should
        not be used and post ballot tasks not run
        """
        importer.current_only = True
        assert importer.force_metadata is False
        importer.do_import(params=None)
        importer.ee_helper.prewarm_cache.assert_called_once_with(current=True)

        expected_url = (
            f"{settings.YNR_BASE}/api/next/ballots/?page_size=200&current=True"
        )
        importer.get_paginator.assert_called_once_with(expected_url)
        importer.add_ballots.assert_called_once()
        # this gets called when current_only used
        importer.run_post_ballot_import_tasks.assert_called()
        importer.delete_orphan_posts.assert_called_once()


class TestYNRBallotImporterDivisionType:
    @pytest.fixture(autouse=True)
    def mock_ee_helper(self, mocker):
        """
        Mocks the EEHelper get_data method
        """
        mocker.patch.object(EEHelper, "get_data", return_value=None)

    @pytest.fixture
    def ballot(self, mocker):
        """
        Returns an unsaved Ballot object with save method on post mocked
        """
        ballot = PostElectionFactory.build(post__division_type="DIW")
        mocker.patch.object(ballot.post, "save")
        return ballot

    def test_set_division_type_unchanged(self, ballot):
        """
        Test that when division_type is set and not a force update, nothing
        happens
        """
        importer = YNRBallotImporter(force_update=False)

        assert importer.set_division_type(ballot=ballot) is None
        assert ballot.post.division_type == "DIW"
        EEHelper.get_data.assert_not_called()
        ballot.post.save.assert_not_called()

    def test_set_division_type_force_no_ee_data(self, ballot):
        """
        Test that force_update ensures update attempt tries, but doesnt change
        when no data
        """
        importer = YNRBallotImporter(force_update=True)

        assert importer.set_division_type(ballot=ballot) is None
        assert ballot.post.division_type == "DIW"
        EEHelper.get_data.assert_called_once_with(ballot.ballot_paper_id)
        ballot.post.save.assert_not_called()

    def test_set_division_type_changed(self, ballot, mocker):
        """
        Test that division_type gets updated
        """
        importer = YNRBallotImporter(force_update=True)
        division = {"division": {"division_type": "NEW"}}
        mocker.patch.object(EEHelper, "get_data", return_value=division)
        mocker.patch.object(ballot.post, "full_clean")

        assert importer.set_division_type(ballot=ballot) is None
        assert ballot.post.division_type == "NEW"
        EEHelper.get_data.assert_called_once_with(ballot.ballot_paper_id)
        ballot.post.full_clean.assert_called_once()
        ballot.post.save.assert_called_once()


class TestYNRPostImporter:
    def test_update_or_create_from_ballot_dict_uses_id(self, mocker):
        ballot_dict = {
            "post": {
                "id": "foo",
                "slug": "bar",
                "label": "example",
            }
        }
        mock = mocker.Mock(return_value=(1, True))
        mocker.patch("elections.models.Post.objects.update_or_create", mock)
        importer = YNRPostImporter()
        importer.update_or_create_from_ballot_dict(ballot_dict=ballot_dict)

        mock.assert_called_once_with(
            ynr_id="foo", defaults={"label": "example"}
        )

    def test_update_or_create_from_ballot_dict_uses_slug(self, mocker):
        ballot_dict = {
            "post": {
                "id": None,
                "slug": "bar",
                "label": "example",
            }
        }
        mock = mocker.Mock(return_value=(1, True))
        mocker.patch("elections.models.Post.objects.update_or_create", mock)
        importer = YNRPostImporter()
        importer.update_or_create_from_ballot_dict(ballot_dict=ballot_dict)

        mock.assert_called_once_with(
            ynr_id="bar", defaults={"label": "example"}
        )
