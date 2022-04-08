import sys
from collections import namedtuple

from core.mixins import ReadFromUrlMixin, ReadFromFileMixin
from core.helpers import twitter_username
from elections.models import PostElection, Election
from parties.models import LocalParty, Manifesto, Party


LocalElection = namedtuple("LocalElection", ["date", "csv_files"])


class LocalPartyImporter(ReadFromUrlMixin, ReadFromFileMixin):

    # TODO check if this need updating
    JOINT_PARTIES = [["party:53", "joint-party:53-119"]]

    def __init__(self, election, force_update=False, from_file=False):
        self.election = election
        self.force_update = force_update
        self.read_from = getattr(self, "read_from_url")
        if from_file:
            self.read_from = getattr(self, "read_from_file")

    def write(self, msg):
        """
        Ensures all outputs include a new line
        """
        sys.stdout.write(f"{msg}\n")

    def delete_parties_for_election_date(self):
        """
        Deletes LocalParty objects associated with elections for the given
        election date
        """
        count, _ = LocalParty.objects.filter(
            post_election__election__election_date=self.election.date,
        ).delete()
        self.write(f"Deleted {count} local parties for {self.election.date}")

    def delete_manifestos_for_election_date(self):
        count, _ = Manifesto.objects.filter(
            election__election_date=self.election.date,
        ).delete()
        self.write(f"Deleted {count} manifestos for {self.election.date}")

    def current_elections(self):
        """
        Checks for current Election objects with the given date
        """
        if self.force_update:
            return True

        return Election.objects.filter(
            current=True, election_date=self.election.date
        ).exists()

    def get_party_list_from_party_id(self, party_id):
        """
        Checks for any joint parties for the given party id
        """
        party_id = f"party:{party_id}"

        for party_list in self.JOINT_PARTIES:
            if party_id in party_list:
                return party_list
        return [party_id]

    def get_parties(self, party_id):
        """
        Return a QuerySet of Party objects for the party_id
        """
        party_list = self.get_party_list_from_party_id(party_id)
        return Party.objects.filter(party_id__in=party_list)

    def get_ballots(self, election_id, parties):
        """
        First checks if the election_id is a special case or is not a full
        election ID e.g. it is made of only two parts such as local.2022-05-05.
        In this case we return all ballots for the type of election and the
        date. Otherwise attempts to find a single PostElection object for the
        election_id. If this does not exist it may be that the ID is the slug
        of an Election object so we return all ballots related to the Election.
        """
        special_cases = ["senedd", "sp", "gla"]
        election_id_list = election_id.split(".")
        election_type = election_id_list[0]
        if len(election_id_list) == 2 or election_type in special_cases:
            ballots = PostElection.objects.filter(
                ballot_paper_id__startswith=f"{election_type}.",
                election__election_date=self.election.date,
            )
        else:
            ballots = PostElection.objects.filter(ballot_paper_id=election_id)

        if not ballots:
            # This might be an election ID, in that case,
            # apply thie row to all post elections without
            # info already
            ballots = PostElection.objects.filter(election__slug=election_id)
        ballots = ballots.filter(personpost__party__in=parties)
        return ballots

    def all_rows(self):
        """
        Yields all CSV rows from multiple files
        """
        for file in self.election.csv_files:
            yield from self.read_from(file)

    def ordered_rows(self):
        """
        Filters out all rows that have no election_id, and then orders remaining
        rows by the number of parts to the ID e.g. local.2022-05-05 would appear
        first, then local.foo.2022-05-05, then local.foo.ward.2022-05-05.
        The reason for this is that we only create one LocalParty for each Party
        and PostElection combination. So if we have a general LocalParty that
        should cover a large set of ballots, we should create these first so
        that if there is a row later on in the spreadsheet with more specific
        details for a LocalParty relating to a PostElection, this will supersede
        the more general one covering the wider range of PostElections.
        """
        rows = filter(lambda row: row["election_id"].strip(), self.all_rows())
        rows = sorted(
            rows, key=lambda row: len(row["election_id"].strip().split("."))
        )
        return rows

    def add_local_party(self, row, party, ballots):
        """
        Takes a row of data, a Party, and a QuerySet of at least one
        PostElection objects, and craetes a LocalParty for each of the ballots.
        """
        twitter = twitter_username(url=row["Twitter"] or "")
        name = self.get_name(row=row)
        # only create local parties for ballots where a candidate is standing
        # for the parent party
        ballots = ballots.filter(personpost__party=party)
        for post_election in ballots:
            country = self.get_country(
                election_type=post_election.election.election_type
            )
            LocalParty.objects.update_or_create(
                parent=party,
                post_election=post_election,
                defaults={
                    "name": name,
                    "twitter": twitter,
                    "facebook_page": row["Facebook"],
                    "homepage": row["Website"],
                    "email": row["Email"],
                    "is_local": country == "Local",
                    "youtube_profile_url": row.get(
                        "Youtube profile", ""
                    ).strip(),
                    "contact_page_url": row.get("Contact page", "").strip(),
                },
            )

        self.write(f"Imported Local Party objects for {name}")

    def get_name(self, row):
        """
        The sheet for Scottish/Welsh/GLA uses "Party Name" header so check for
        both
        """
        return row.get("Local party name", row.get("Party name"))

    def import_parties(self):
        """
        This is the main action that is run by the class. First existing
        LocalParty objects for an election are deleted. Then it validates the
        row contains data we can use. Then adds a LocalParty object for each
        parent party.
        """
        self.delete_parties_for_election_date()
        self.delete_manifestos_for_election_date()

        if not self.current_elections():
            self.write(
                f"No current elections for {self.election.date}, skipping"
            )
            return

        for row in self.ordered_rows():
            name = self.get_name(row=row)
            party_id = (row["party_id"] or "").strip()
            if not party_id or not name:
                self.write("Missing data, skipping row")
                continue

            parties = self.get_parties(party_id=party_id)
            if not parties:
                self.write(f"Parent party not found with IDs {party_id}")
                continue

            ballots = self.get_ballots(
                election_id=row["election_id"].strip(), parties=parties
            )
            if not ballots:
                self.write("Skipping as no ballots to use")
                continue

            for party in parties:
                self.add_local_party(row, party, ballots)
                elections = ballots.values_list(
                    "election__slug", flat=True
                ).distinct()
                manifesto_web = row.get("Manifesto Website URL", "").strip()
                manifesto_pdf = row.get("Manifesto PDF URL", "").strip()
                if not any([manifesto_web, manifesto_pdf]):
                    self.write("No links to create Manifesto, skipping")
                    continue

                for slug in elections:
                    election = Election.objects.get(slug=slug)
                    self.add_manifesto(row, party, election)

    def get_country(self, election_type):
        country_mapping = {
            "local": "Local",
            "senedd": "Wales",
            "sp": "Scotland",
        }
        return country_mapping.get(election_type, "UK")

    def add_manifesto(self, row, party, election):
        manifesto_web = row.get("Manifesto Website URL", "").strip()
        manifesto_pdf = row.get("Manifesto PDF URL", "").strip()
        country = self.get_country(election_type=election.election_type)
        language = row.get("Manifesto Language", "English").strip()
        easy_read_url = row.get("Manifesto Easy Read PDF", "").strip()
        if any([manifesto_web, manifesto_pdf]):
            manifesto_obj, created = Manifesto.objects.update_or_create(
                election=election,
                party=party,
                country=country,
                language=language or "English",
                defaults={
                    "web_url": manifesto_web,
                    "pdf_url": manifesto_pdf,
                    "easy_read_url": easy_read_url,
                },
            )
            manifesto_obj.save()
            self.write(f"{'Created' if created else 'Updated'} {manifesto_obj}")
