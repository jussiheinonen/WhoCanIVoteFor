import pytest
from elections.tests.factories import (
    PostElectionFactory,
    ElectionFactoryLazySlug,
)
from elections.management.commands.import_ballots import Command


class TestPopulateAnyNonByElections:
    @pytest.mark.django_db
    def test_any_non_by_elections_true_with_mix(self):
        """
        When an election contains any non by-election ballots then
        the Election.any_non_by_elections is True
        """
        election = ElectionFactoryLazySlug(any_non_by_elections=False)
        PostElectionFactory.create_batch(
            size=20,
            election=election,
        )
        PostElectionFactory(
            ballot_paper_id="foo.local.by.2021-05-06", election=election
        )
        cmd = Command()
        cmd.populate_any_non_by_elections_field()
        election.refresh_from_db()
        assert election.any_non_by_elections is True

    @pytest.mark.django_db
    def test_any_non_by_elections_false(self):
        """
        When an election contains only by-election ballots then
        the Election.any_non_by_elections is False
        """
        election = ElectionFactoryLazySlug(any_non_by_elections=False)
        PostElectionFactory(
            ballot_paper_id="foo.local.by.2021-05-06", election=election
        )
        cmd = Command()
        cmd.populate_any_non_by_elections_field()
        election.refresh_from_db()
        assert election.any_non_by_elections is False

    @pytest.mark.django_db
    def test_any_non_by_elections_true_without_by_election(self):
        """
        When an election contains only non by-election ballots then
        the Election.any_non_by_elections is True
        """
        election = ElectionFactoryLazySlug(any_non_by_elections=False)
        PostElectionFactory.create_batch(
            size=20,
            election=election,
        )
        cmd = Command()
        cmd.populate_any_non_by_elections_field()
        election.refresh_from_db()
        assert election.any_non_by_elections is True
