# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from tqdm import tqdm


# Imports from geography.
from geography.management.commands.bootstrap._arguments import ArgumentsMethods
from geography.management.commands.bootstrap._attributes import Attributes
from geography.management.commands.bootstrap._toposimplify import Toposimplify
from geography.management.commands.bootstrap.aggregate_shapes.district import (
    DistrictCountyShapes,
)
from geography.management.commands.bootstrap.aggregate_shapes.state import (
    StateCountyShapes,
    StateDistrictShapes,
    StateTownshipShapes,
)
from geography.management.commands.bootstrap.download import DownloadCounty
from geography.management.commands.bootstrap.download import DownloadDistrict
from geography.management.commands.bootstrap.download import DownloadState
from geography.management.commands.bootstrap.download import DownloadTownship
from geography.management.commands.bootstrap.fixtures import CountyFixtures
from geography.management.commands.bootstrap.fixtures import DistrictFixtures
from geography.management.commands.bootstrap.fixtures import NationFixtures
from geography.management.commands.bootstrap.fixtures import StateFixtures


class Command(
    ArgumentsMethods,
    Attributes,
    Toposimplify,
    DownloadState,
    DownloadCounty,
    DownloadDistrict,
    DownloadTownship,
    CountyFixtures,
    DistrictFixtures,
    NationFixtures,
    StateFixtures,
    StateCountyShapes,
    StateDistrictShapes,
    StateTownshipShapes,
    DistrictCountyShapes,
    BaseCommand,
):
    help = (
        "Downloads and bootstraps geographic data for states, congressional "
        "districts, counties and townships from the U.S. Census Bureau "
        "simplified cartographic boundary files."
    )

    def handle(self, *args, **options):
        self.set_attributes()
        self.parse_arguments(options)

        tqdm.write("🌎  BOOTSTRAPING GEOGRAPHY 🌎")
        tqdm.write("(Get a ☕ . This will take a few minutes.)\n")
        tqdm.write("Downloading data 📡")
        self.download_state_data()
        self.download_district_data()
        self.download_county_data()
        self.download_township_data()
        self.stdout.write(self.style.SUCCESS("Done.\n"))

        tqdm.write("Creating fixtures 🌐")
        self.create_nation_fixtures()
        self.create_state_fixtures()
        self.create_district_fixtures()
        self.create_county_fixtures()

        self.stdout.write(self.style.SUCCESS("All done! 🏁"))
