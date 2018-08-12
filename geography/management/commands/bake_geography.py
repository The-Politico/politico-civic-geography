from tqdm import tqdm

from django.core.management.base import BaseCommand

from .bake._arguments import ArgumentsMethods
from .bake._attributes import Attributes
from .bake.geometries import DistrictGeometries, StateGeometries


class Command(
    ArgumentsMethods,
    Attributes,
    StateGeometries,
    DistrictGeometries,
    BaseCommand,
):
    help = (
        "Uploads topojson files by state and district to an Amazon S3 bucket."
    )

    def handle(self, *args, **options):
        self.parse_arguments(options)
        self.set_attributes()

        tqdm.write("🌎  BAKING GEOGRAPHY 🌎\n")

        self.bake_state_geometries()
        self.bake_district_geometries()

        self.stdout.write(self.style.SUCCESS("All done! 🏁"))
