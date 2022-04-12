import pytest

from elections.models import PostElection
from parties.models import Party
from people.management.commands.import_people import Command
from people.models import Person, PersonPost


class TestUpdateCandidacies:
    @pytest.fixture
    def person_data(self):
        return {
            "candidacies": [
                {
                    "elected": False,
                    "party_list_position": 1,
                    "party": {
                        "url": "http://candidates.democracyclub.org.uk/api/next/parties/PP53/",
                        "ec_id": "PP53",
                        "name": "Labour Party",
                        "legacy_slug": "party:53",
                    },
                    "party_name": "Labour Party",
                    "party_description_text": "Labour Party",
                    "ballot": {
                        "url": "http://candidates.democracyclub.org.uk/api/next/ballots/parl.romsey-and-southampton-north.2010-05-06/",
                        "ballot_paper_id": "parl.romsey-and-southampton-north.2010-05-06",
                    },
                    "previous_party_affiliations": [],
                },
                {
                    "elected": False,
                    "party_list_position": None,
                    "party": {
                        "url": "http://candidates.democracyclub.org.uk/api/next/parties/PP53/",
                        "ec_id": "PP53",
                        "name": "Labour Party",
                        "legacy_slug": "party:53",
                        "created": "2022-02-16T16:23:03.962770Z",
                        "modified": "2022-03-10T10:12:26.510945Z",
                    },
                    "party_name": "Labour Party",
                    "party_description_text": "Labour Party",
                    "created": "2022-03-16T11:25:42.328768Z",
                    "modified": "2022-03-17T12:36:20.946155Z",
                    "ballot": {
                        "url": "http://candidates.democracyclub.org.uk/api/next/ballots/local.cardiff.gabalfa.2022-05-05/",
                        "ballot_paper_id": "local.cardiff.gabalfa.2022-05-05",
                    },
                    "previous_party_affiliations": [
                        {
                            "url": "http://candidates.democracyclub.org.uk/api/next/parties/ynmp-party:2/",
                            "ec_id": "ynmp-party:2",
                            "name": "Independent",
                            "legacy_slug": "ynmp-party:2",
                            "created": "2022-02-16T15:39:15.647123Z",
                            "modified": "2022-02-16T17:13:11.323855Z",
                        }
                    ],
                },
            ],
        }

    def test_update_candidacies(self, person_data, mocker):
        person_obj = mocker.MagicMock(spec=Person)
        candidacy_one = mocker.MagicMock(spec=PersonPost)
        candidacy_two = mocker.MagicMock(spec=PersonPost)
        person_obj.personpost_set.update_or_create.side_effect = [
            (candidacy_one, True),
            (candidacy_two, True),
        ]
        first_ballot = mocker.MagicMock(
            spec=PostElection,
            ballot_paper_id="parl.romsey-and-southampton-north.2010-05-06",
        )
        second_ballot = mocker.MagicMock(
            spec=PostElection,
            ballot_paper_id="local.cardiff.gabalfa.2022-05-05",
        )
        mock_party = mocker.MagicMock()
        mocker.patch.object(
            PostElection.objects,
            "get",
            side_effect=[first_ballot, second_ballot],
        )
        mocker.patch.object(Party.objects, "get", return_value=mock_party)

        command = Command()
        command.update_candidacies(
            person_data=person_data,
            person_obj=person_obj,
        )

        expected_calls = [
            mocker.call(
                post_election=first_ballot,
                post=first_ballot.post,
                election=first_ballot.election,
                defaults={
                    "party_id": "party:53",
                    "list_position": 1,
                    "elected": False,
                    "party_name": "Labour Party",
                    "party_description_text": "Labour Party",
                },
            ),
            mocker.call(
                post_election=second_ballot,
                post=second_ballot.post,
                election=second_ballot.election,
                defaults={
                    "party_id": "party:53",
                    "list_position": None,
                    "elected": False,
                    "party_name": "Labour Party",
                    "party_description_text": "Labour Party",
                },
            ),
        ]
        person_obj.personpost_set.update_or_create.assert_has_calls(
            expected_calls
        )
        candidacy_one.previous_party_affiliations.add.assert_not_called()
        candidacy_two.previous_party_affiliations.add.assert_called_once_with(
            mock_party
        )
        Party.objects.get.assert_called_once_with(party_id="ynmp-party:2")

    def test_delete_old_candidacies(self, person_data, mocker):
        person_obj = mocker.MagicMock(spec=Person)
        delete = mocker.MagicMock(return_value=({}, False))
        person_obj.personpost_set.exclude.return_value.delete = delete

        command = Command()
        command.delete_old_candidacies(
            person_data=person_data, person_obj=person_obj
        )

        person_obj.personpost_set.exclude.assert_called_once_with(
            post_election__ballot_paper_id__in=[
                "parl.romsey-and-southampton-north.2010-05-06",
                "local.cardiff.gabalfa.2022-05-05",
            ]
        )
        delete.assert_called_once()
