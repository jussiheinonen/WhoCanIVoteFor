from dateutil.parser import parse

from django.core.management.base import BaseCommand
from django.db import transaction
from elections.import_helpers import time_function_length

from parties.importers import LocalPartyImporter, LocalElection


class Command(BaseCommand):
    ELECTIONS = [
        LocalElection(
            date="2018-05-03",
            csv_files=[
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3pC0vtT9WaCyKDzqARQZY6aoYCyKZLyIvumKaX3TpqG0rt4y0fXp6dOPOZGMX6v0dFczHfizwidwZ/pub?gid=582783400&single=true&output=csv",
            ],
        ),
        LocalElection(
            date="2019-05-02",
            csv_files=[
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vTO-z37bBMxKwCuORIl2vE8v0kMFHlHETvBhGjuDidM1Wy4QxQawRou53kNLjEiJmpMhebRqoWZL9s-/pub?gid=0&single=true&output=csv",
            ],
        ),
        LocalElection(
            date="2021-05-06",
            csv_files=[
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vQx49JTec8i5oz_x6SJanvSKPc8BccanIlnGR4j0plbD99QFslXw7JEvWSNtdrJiePBMBi0AXkvw3e7/pub?gid=1210343217&single=true&output=csv",
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vQx49JTec8i5oz_x6SJanvSKPc8BccanIlnGR4j0plbD99QFslXw7JEvWSNtdrJiePBMBi0AXkvw3e7/pub?gid=2091491905&single=true&output=csv",
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vQx49JTec8i5oz_x6SJanvSKPc8BccanIlnGR4j0plbD99QFslXw7JEvWSNtdrJiePBMBi0AXkvw3e7/pub?gid=1013163356&single=true&output=csv",
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vQx49JTec8i5oz_x6SJanvSKPc8BccanIlnGR4j0plbD99QFslXw7JEvWSNtdrJiePBMBi0AXkvw3e7/pub?gid=1273833263&single=true&output=csv",
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vQe-g_2T25Hal_utsq0cZ67UdT9SEeKi3EfY2aMWqxtkhQle16uMc_SVrX1g7T6ZQfMeDqvwF3ZTyc1/pub?gid=0&single=true&output=csv",
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vQe-g_2T25Hal_utsq0cZ67UdT9SEeKi3EfY2aMWqxtkhQle16uMc_SVrX1g7T6ZQfMeDqvwF3ZTyc1/pub?gid=1314966429&single=true&output=csv",
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vQe-g_2T25Hal_utsq0cZ67UdT9SEeKi3EfY2aMWqxtkhQle16uMc_SVrX1g7T6ZQfMeDqvwF3ZTyc1/pub?gid=1067010902&single=true&output=csv",
            ],
        ),
        LocalElection(
            date="2022-05-05",
            csv_files=[
                # NI
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxlunnk3ORlLg0CSBArM1GcRh09VPJH5b7k_biArGq3XewoLd4UZylvmcWWgNuAsn2jCPTLr2Rns3J/pub?gid=0&single=true&output=csv",
                # locals - global
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vS1fmfKixgnFKoGEiaa87HIeQrEnjPmz9Xs9ypDdh4Z-4xcv2oxUT3AB9dgcajPPMFMV3d_3ephmdcH/pub?gid=0&single=true&output=csv",
                # Eng - conservaties
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1SnO25tI8NQ-D-me4DKkiuJfo_eY0jdRooHcsuHRM7a4s0sWntMF42CqvRRqkyMPlx3CL-ppoqAVp/pub?gid=457381042&single=true&output=csv",
                # Eng - labour
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1SnO25tI8NQ-D-me4DKkiuJfo_eY0jdRooHcsuHRM7a4s0sWntMF42CqvRRqkyMPlx3CL-ppoqAVp/pub?gid=1580819525&single=true&output=csv",
                # Eng - lib dems
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1SnO25tI8NQ-D-me4DKkiuJfo_eY0jdRooHcsuHRM7a4s0sWntMF42CqvRRqkyMPlx3CL-ppoqAVp/pub?gid=41026214&single=true&output=csv",
                # Eng - greens
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1SnO25tI8NQ-D-me4DKkiuJfo_eY0jdRooHcsuHRM7a4s0sWntMF42CqvRRqkyMPlx3CL-ppoqAVp/pub?gid=1806274182&single=true&output=csv",
                # Eng - other parties
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1SnO25tI8NQ-D-me4DKkiuJfo_eY0jdRooHcsuHRM7a4s0sWntMF42CqvRRqkyMPlx3CL-ppoqAVp/pub?gid=1274679305&single=true&output=csv",
                # London - cons
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYHiMeM5pm4kJBejdsYvgS1GjXSHFkj143ANhpz4hZeQ2RYRCRCLUavbswpfKAP_zvIUiFRJpsZPO0/pub?gid=1817827560&single=true&output=csv",
                # London - Lab
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYHiMeM5pm4kJBejdsYvgS1GjXSHFkj143ANhpz4hZeQ2RYRCRCLUavbswpfKAP_zvIUiFRJpsZPO0/pub?gid=98621569&single=true&output=csv",
                # London - Lib Dems
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYHiMeM5pm4kJBejdsYvgS1GjXSHFkj143ANhpz4hZeQ2RYRCRCLUavbswpfKAP_zvIUiFRJpsZPO0/pub?gid=1901014574&single=true&output=csv",
                # London - Greens
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYHiMeM5pm4kJBejdsYvgS1GjXSHFkj143ANhpz4hZeQ2RYRCRCLUavbswpfKAP_zvIUiFRJpsZPO0/pub?gid=954903673&single=true&output=csv",
                # London - Others
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYHiMeM5pm4kJBejdsYvgS1GjXSHFkj143ANhpz4hZeQ2RYRCRCLUavbswpfKAP_zvIUiFRJpsZPO0/pub?gid=675723772&single=true&output=csv",
                # Scotland - Cons
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vTE4PeVOL00STx_lLmCYWX4pTYnhDJFWvFkImlcj95YYWzVbsz8rF2W6kvCVyElZSpr8zqXPahy6Z-G/pub?gid=1657757536&single=true&output=csv",
                # Scotland - Lab
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vTE4PeVOL00STx_lLmCYWX4pTYnhDJFWvFkImlcj95YYWzVbsz8rF2W6kvCVyElZSpr8zqXPahy6Z-G/pub?gid=1472367348&single=true&output=csv",
                # Scotland - Greens
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vTE4PeVOL00STx_lLmCYWX4pTYnhDJFWvFkImlcj95YYWzVbsz8rF2W6kvCVyElZSpr8zqXPahy6Z-G/pub?gid=1420950884&single=true&output=csv",
                # Scotland - SNP
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vTE4PeVOL00STx_lLmCYWX4pTYnhDJFWvFkImlcj95YYWzVbsz8rF2W6kvCVyElZSpr8zqXPahy6Z-G/pub?gid=1791553048&single=true&output=csv",
                # Scotland - other
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vTE4PeVOL00STx_lLmCYWX4pTYnhDJFWvFkImlcj95YYWzVbsz8rF2W6kvCVyElZSpr8zqXPahy6Z-G/pub?gid=1286661054&single=true&output=csv",
                # Wales - Cons
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_GlefU9m8B5CPGeysNg0WWMAxv_4ed9TU29Q_w1jW_crRC93_IPd-UigLBLms_EMeuqKL0XvfvbDf/pub?gid=1664580048&single=true&output=csv",
                # Wales - Lab
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_GlefU9m8B5CPGeysNg0WWMAxv_4ed9TU29Q_w1jW_crRC93_IPd-UigLBLms_EMeuqKL0XvfvbDf/pub?gid=1751255273&single=true&output=csv",
                # Wales - Lib dems
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_GlefU9m8B5CPGeysNg0WWMAxv_4ed9TU29Q_w1jW_crRC93_IPd-UigLBLms_EMeuqKL0XvfvbDf/pub?gid=2131868538&single=true&output=csv",
                # Wales - Greens
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_GlefU9m8B5CPGeysNg0WWMAxv_4ed9TU29Q_w1jW_crRC93_IPd-UigLBLms_EMeuqKL0XvfvbDf/pub?gid=1565590221&single=true&output=csv",
                # Wales - Plaid Cymru
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_GlefU9m8B5CPGeysNg0WWMAxv_4ed9TU29Q_w1jW_crRC93_IPd-UigLBLms_EMeuqKL0XvfvbDf/pub?gid=935387408&single=true&output=csv",
                # Wales - others
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_GlefU9m8B5CPGeysNg0WWMAxv_4ed9TU29Q_w1jW_crRC93_IPd-UigLBLms_EMeuqKL0XvfvbDf/pub?gid=1603267768&single=true&output=csv",
            ],
        ),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force-update",
            action="store_true",
            help="Will update regardless of whether there are current elections for the date",
        )
        parser.add_argument(
            "-ff",
            "--from-file",
            nargs=2,
            metavar=("election_date", "path_to_file"),
            help="To import from a file, pass in an election date and the path to the file",
        )

    def valid_date(self, value):
        return parse(value)

    def import_from_file(self):
        """
        Runs the importer for the file passed in arguments
        """
        date, filepath = self.options["from_file"]
        if not self.valid_date(value=date):
            self.stdout.write("Date is invalid")
            return

        election = LocalElection(date=date, csv_files=[filepath])
        importer = LocalPartyImporter(
            election=election,
            force_update=self.options["force_update"],
            from_file=True,
        )
        importer.import_parties()

    def import_from_elections(self):
        """
        Runs the importer for all elections in the ELECTIONS list. This is the
        default method of running the import process
        """
        for election in self.ELECTIONS:
            importer = LocalPartyImporter(
                election=election,
                force_update=self.options["force_update"],
            )
            importer.import_parties()

    @time_function_length
    @transaction.atomic
    def handle(self, **options):
        self.options = options

        if options["from_file"]:
            return self.import_from_file()

        self.import_from_elections()
