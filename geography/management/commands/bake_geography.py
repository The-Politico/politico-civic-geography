# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from tqdm import tqdm


# Imports from geography.
from geography.management.commands.bake._arguments import ArgumentsMethods
from geography.management.commands.bake._attributes import Attributes
from geography.management.commands.bake.geometries import DistrictGeometries
from geography.management.commands.bake.geometries import StateGeometries


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
