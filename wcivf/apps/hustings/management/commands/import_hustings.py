"""
Importer for all our important Hustings data
"""
import os
import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from elections.models import PostElection
from hustings.models import Husting
from hustings.importers import HustingImporter


def dt_from_string(dt):
    """
    Given a date string DT, return a datetime object.
    """
    try:
        date = datetime.datetime.strptime(dt, "%Y-%m-%d")
    except ValueError:
        pass
    except TypeError:
        return None
    else:
        return timezone.make_aware(date, timezone.get_current_timezone())

    # kept for legacy reasons - previous years used different date formatting
    try:
        date = datetime.datetime.strptime(dt, "%Y-%b-%d")
    except ValueError:
        date = datetime.datetime.strptime(dt, "%Y-%B-%d")

    return timezone.make_aware(date, timezone.get_current_timezone())


def stringy_time_to_inty_time(stringy_time):
    """
    Given a string in the form HH:MM return integer values for hour
    and minute.
    """
    hour, minute = stringy_time.split(":")
    return int(hour), int(minute)


def set_time_string_on_datetime(dt, time_string):
    """
    Given a datetime DT and a string in the form HH:MM return a
    new datetime with the hour and minute set according to
    TIME_STRING
    """
    hour, minute = stringy_time_to_inty_time(time_string)
    dt = dt.replace(hour=hour, minute=minute)
    return dt


class Command(BaseCommand):

    URLS = [
        # NI
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_VvyPiJA75yOCv7j_E0PjZe3yFy77C9RH9ucb1bM2_QBhSIWSRKsF3_qhcukrxQsRMu9SRyNXWX05/pub?gid=372490874&single=true&output=csv",
        # ENG MAYORS
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_VvyPiJA75yOCv7j_E0PjZe3yFy77C9RH9ucb1bM2_QBhSIWSRKsF3_qhcukrxQsRMu9SRyNXWX05/pub?gid=1086162179&single=true&output=csv",
        # ENG LOCALS
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_VvyPiJA75yOCv7j_E0PjZe3yFy77C9RH9ucb1bM2_QBhSIWSRKsF3_qhcukrxQsRMu9SRyNXWX05/pub?gid=1180606386&single=true&output=csv",
        # SCOT LOCALS
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_VvyPiJA75yOCv7j_E0PjZe3yFy77C9RH9ucb1bM2_QBhSIWSRKsF3_qhcukrxQsRMu9SRyNXWX05/pub?gid=976193034&single=true&output=csv",
        # WALES LOCALS
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_VvyPiJA75yOCv7j_E0PjZe3yFy77C9RH9ucb1bM2_QBhSIWSRKsF3_qhcukrxQsRMu9SRyNXWX05/pub?gid=2061283903&single=true&output=csv",
        # BY-ELECTIONS
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_VvyPiJA75yOCv7j_E0PjZe3yFy77C9RH9ucb1bM2_QBhSIWSRKsF3_qhcukrxQsRMu9SRyNXWX05/pub?gid=1279122722&single=true&output=csv",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            required=False,
            help="Path to the file with the hustings in it",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            dest="quiet",
            default=False,
            help="Only output errors",
        )
        parser.add_argument(
            "--urls",
            "-u",
            dest="urls",
            nargs="+",
            required=False,
            help="Specify a URLs to a google sheet to import from",
        )

    def create_husting(self, row):
        """
        Create an individual husting
        """
        # kept the second option to work with previous years spreadsheets
        starts = row.get("Date (YYYY-MM-DD)") or row.get("Date (YYYY-Month-DD)")
        starts = dt_from_string(starts)
        if not starts:
            return None

        ends = None
        if row["Start time (00:00)"]:
            starts = set_time_string_on_datetime(
                starts, row["Start time (00:00)"]
            )
        if row["End time (if known)"]:
            ends = set_time_string_on_datetime(
                starts, row["End time (if known)"]
            )

        # Get the post_election
        pes = PostElection.objects.filter(ballot_paper_id=row["Election ID"])
        if not pes.exists():
            # This might be a parent election ID
            pes = PostElection.objects.filter(election__slug=row["Election ID"])
        for pe in pes:
            husting = Husting.objects.create(
                post_election=pe,
                title=row["Title of event"],
                url=row["Link to event information"],
                starts=starts,
                ends=ends,
                location=row.get("Name of event location (e.g. Church hall)"),
                postcode=row.get("Postcode of event location"),
                postevent_url=row[
                    "Link to post-event information (e.g. blog post, video)"
                ],
            )
            return husting

    def import_hustings(self):
        for row in self.importer.rows:
            try:
                husting = self.create_husting(row)
            except ValueError as e:
                self.stdout.write(repr(e))
                husting = None

            if not husting:
                self.stdout.write(f"Couldn't create {row['Title of event']}")
                continue

            self.hustings_counter += 1
            self.stdout.write(
                "Created husting {0} <{1}>".format(
                    self.hustings_counter, husting.post_election.ballot_paper_id
                )
            )

    @transaction.atomic
    def handle(self, **options):
        """
        Entry point for our command.
        """
        if options["quiet"]:
            self.stdout = open(os.devnull, "w")

        file = options["filename"]
        if file:
            answer = input(
                "All hustings will be deleted and replaced with only those included in the file proved. Do you want to continue? y/n\n"
            )
            if answer != "y":
                return

        count, _ = Husting.objects.all().delete()
        self.stdout.write(f"Deleting {count} Husting objects")

        self.hustings_counter = 0
        if file:
            self.importer = HustingImporter(file_path=options["filename"])
            return self.import_hustings()

        urls = options["urls"] or self.URLS
        for url in urls:
            self.importer = HustingImporter(url=url)
            self.import_hustings()
