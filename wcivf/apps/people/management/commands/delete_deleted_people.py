from django.core.management.base import BaseCommand
from django.utils import timezone

from people.import_helpers import YNRPersonImporter


class Command(BaseCommand):
    help = "Deletes People objects that have been delted in YNR"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            action="store",
            dest="date",
            default=False,
            help="The date to look for deleted people. If not used defaults to today",
        )

    def handle(self, **options):
        date = options["date"] or timezone.now().date()
        importer = YNRPersonImporter(
            params={
                "created": str(date),
                "action_type": "person-delete",
            }
        )
        importer.delete_deleted_people()
