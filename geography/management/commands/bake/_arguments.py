class ArgumentsMethods(object):
    def parse_arguments(self, options):
        self.YEAR = options["year"]
        self.STATES = options["states"]

    def add_arguments(self, parser):
        parser.add_argument(
            "states",
            nargs="+",
            help="States to export by FIPS code. \
            Use 00 to export all geographies.",
        )

        parser.add_argument(
            "--year",
            action="store",
            dest="year",
            default="2018",
            help="Specify year of shapefile series (default, 2018)",
        )
