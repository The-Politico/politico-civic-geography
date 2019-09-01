# Imports from Django.
from django.core.management.base import CommandError


class ArgumentsMethods(object):
    def parse_arguments(self, options):
        self.YEAR = options["year"]
        self.CONGRESS = options["congress"]
        self.THRESHOLDS = {
            "nation": str(options["nationThreshold"]),
            "state": str(options["stateThreshold"]),
            "district": str(options["districtThreshold"]),
            "county": str(options["countyThreshold"]),
        }

    def add_arguments(self, parser):
        def check_threshold(arg):
            value = float(arg)
            if value < 0 or value > 1:
                raise CommandError(
                    "Threshold must be a decimal between 0 and 1."
                )
            return value

        parser.add_argument(
            "--year",
            action="store",
            dest="year",
            default="2018",
            help="Specify year of shapefile series (default, 2018)",
        )
        parser.add_argument(
            "--congress",
            action="store",
            dest="congress",
            default="116",
            help="Specify congress of district shapefile series \
             (default, 116)",
        )
        parser.add_argument(
            "--nationThreshold",
            type=check_threshold,
            default=0.005,
            dest="nationThreshold",
            help="Simplification threshold value for nation topojson \
                (default, 0.005)",
        )
        parser.add_argument(
            "--stateThreshold",
            type=check_threshold,
            default=0.05,
            dest="stateThreshold",
            help="Simplification threshold value for state topojson \
                (default, 0.05)",
        )
        parser.add_argument(
            "--districtThreshold",
            type=check_threshold,
            default=0.08,
            dest="districtThreshold",
            help="Simplification threshold value for district topojson \
                (default, 0.08)",
        )
        parser.add_argument(
            "--countyThreshold",
            type=check_threshold,
            default=0.075,
            dest="countyThreshold",
            help="Simplification threshold value for county topojson \
                (default, 0.075)",
        )
