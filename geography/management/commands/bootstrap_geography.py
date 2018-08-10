from tqdm import tqdm

from django.core.management.base import BaseCommand

from .bootstrap._arguments import ArgumentsMethods
from .bootstrap._attributes import Attributes
from .bootstrap._toposimplify import Toposimplify
from .bootstrap.download import (DownloadCounty, DownloadDistrict,
                                 DownloadState, DownloadTownship)
from .bootstrap.fixtures import (CountyFixtures, DistrictFixtures,
                                 NationFixtures, StateFixtures)
from .bootstrap.shapes import CountyShape, DistrictShape, TownshipShape


class Command(
    ArgumentsMethods, Attributes, Toposimplify,
    DownloadState, DownloadCounty, DownloadDistrict, DownloadTownship,
    CountyFixtures, DistrictFixtures, NationFixtures, StateFixtures,
    CountyShape, DistrictShape, TownshipShape,
    BaseCommand
):
    help = (
        'Downloads and bootstraps geographic data for states and counties '
        'from the U.S. Census Bureau simplified cartographic boundary files.'
    )

    def handle(self, *args, **options):
        self.set_attributes()
        self.parse_arguments(options)

        tqdm.write('Downloading data')
        self.download_state_data()
        self.download_district_data()
        self.download_county_data()
        self.download_township_data()

        tqdm.write('Creating fixtures')
        self.create_nation_fixtures()
        self.create_state_fixtures()
        self.create_district_fixtures()
        self.create_county_fixtures()

        self.stdout.write(
            self.style.SUCCESS('All done! 🏁')
        )
