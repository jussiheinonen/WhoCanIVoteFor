from referendums.models import Referendum
from elections.models import Election, PostElection
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
    Creates an Election, PostElection and Referendum object
    Example usage:
    python manage.py add_referendum -e ref.croydon.2021-10-07 \
        -p gss:E14000654 \
        -n 'Croydon Governance Referendum' \
        -q 'How would you like the London Borough of Croydon to be run?' \
        -a1 'By a leader who is an elected councillor chosen by a vote of the other elected councillors. This is how the council is run now.' \
        -a2 'By a mayor who is elected by voters. This would be a change from how the council is run now.' \
        g'
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            "--election-id",
            dest="election_id",
            action="store",
            help="The election ID as set in EE",
            required=True,
        )

        parser.add_argument(
            "-n",
            "--name",
            dest="name",
            action="store",
            help="Election name",
            required=True,
        )

        # Post is a non-nullable field on PostElection so this is required
        # but unclear if we will always have one for a referendum?
        parser.add_argument(
            "-p",
            "--post-id",
            dest="post_id",
            action="store",
            help="The ID for post to be used for the referendum",
            required=True,
        )

        parser.add_argument(
            "-q",
            "--question",
            dest="question",
            action="store",
            help="The question of the referendum",
            required=True,
        )

        parser.add_argument(
            "-a1",
            "--answer-one",
            dest="answer_one",
            action="store",
            help="The first answer on the ballot",
            required=True,
        )

        parser.add_argument(
            "-a2",
            "--answer-two",
            dest="answer_two",
            action="store",
            help="The second answer on the ballot",
            required=True,
        )

        parser.add_argument(
            "-url",
            "--council-url",
            dest="council_url",
            action="store",
            help="The url to the council page about the referendum",
            default="",
            required=False,
        )

    def handle(self, **options):
        election_id = options["election_id"]
        election_date = election_id.split(".")[-1]

        election, created = Election.objects.update_or_create(
            slug=election_id,
            defaults={
                "election_date": election_date,
                "current": True,
                "election_type": "ref",
                "election_weight": 100,  # taken from YNRElectionImporter.ballot_order charisma_map
                "name": options["name"],
                "any_non_by_elections": True,
            },
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {election}")

        ballot, created = PostElection.objects.update_or_create(
            ballot_paper_id=election_id,
            defaults={
                "post_id": options["post_id"],
                "election": election,
            },
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {ballot}")

        council_name = election_id.split(".")[1].title()
        referendum, created = Referendum.objects.update_or_create(
            ballot=ballot,
            defaults={
                "question": options["question"],
                "date": election_date,
                "council_name": council_name,
                "answer_one": options["answer_one"],
                "answer_two": options["answer_two"],
                "council_url": options["council_url"],
            },
        )
        self.stdout.write(f"{'Created' if created else 'Updated'} {referendum}")
