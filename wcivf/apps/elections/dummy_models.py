from datetime import date

from elections.models import Election, Post, PostElection
from people.dummy_models import DummyCandidacy, DummyPerson


class DummyPostElection(PostElection):
    party_ballot_count = 5
    display_as_party_list = False

    election = Election(
        name="Llantalbot local election",
        election_date=date(2022, 5, 5),
        any_non_by_elections=True,
    )
    post = Post(label="Made-Up-Ward")

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ballot_paper_id = "local.faketown.made-up-ward.2022-05-05"
        self.election.get_absolute_url = self.election_get_absolute_url

    def election_get_absolute_url(self):
        return ""

    def people(self):
        return [
            DummyCandidacy(
                person=DummyPerson(
                    name="Jimmy Jordan", favourite_biscuit="Jaffa cake"
                ),
                election=self.election,
                party_name="Yellow Party",
            ),
            DummyCandidacy(
                person=DummyPerson(
                    name="Rhuanedd Llewelyn",
                    favourite_biscuit="Chocolate digestive",
                ),
                election=self.election,
                party_name="Independent",
            ),
            DummyCandidacy(
                person=DummyPerson(
                    name="Ryan Evans", favourite_biscuit="Party ring"
                ),
                election=self.election,
                party_name="Lilac Party",
            ),
            DummyCandidacy(
                person=DummyPerson(
                    name="Sarah Jarman", favourite_biscuit="Hobnob"
                ),
                election=self.election,
                party_name="Purple Party",
            ),
            DummyCandidacy(
                person=DummyPerson(
                    name="Sofia Williamson",
                    favourite_biscuit="Custard cream",
                ),
                election=self.election,
                party_name="Independent",
            ),
        ]
