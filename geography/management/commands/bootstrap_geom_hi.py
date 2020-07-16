# Imports from python.
import os


# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
import geojson
import shapefile


# Imports from geography.
from geography.management.commands.bootstrap._arguments import ArgumentsMethods
from geography.management.commands.bootstrap._attributes import Attributes
from geography.management.commands.bootstrap._toposimplify import Toposimplify
from geography.models import Division
from geography.models import DivisionLevel
from geography.models import Geometry
from geography.utils.lookups import county_lookup


SHP_SLUG = "clipped_hi"
STATE_LEVEL = DivisionLevel.STATE


class Command(Toposimplify, ArgumentsMethods, Attributes, BaseCommand):
    def get_county_shp(self, fips):
        cmd_path = os.path.dirname(os.path.realpath(__file__))
        SHAPEFILE_PATH = os.path.join(cmd_path, "../../bin/hi")

        shape = shapefile.Reader(
            os.path.join(SHAPEFILE_PATH, "{}.shp".format(SHP_SLUG))
        )
        fields = shape.fields[1:]
        field_names = [f[0] for f in fields]

        county_records = [
            shp
            for shp in shape.shapeRecords()
            if dict(zip(field_names, shp.record))["STATEFP"] == fips
        ]
        features = []
        for shp in county_records:
            rec = dict(zip(field_names, shp.record))
            geometry = shp.shape.__geo_interface__
            geodata = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "state": rec["STATEFP"],
                    "county": rec["COUNTYFP"],
                    "name": county_lookup[rec["STATEFP"]].get(
                        rec["COUNTYFP"], rec["NAME"]
                    ),
                },
            }
            features.append(geodata)
        threshold = (
            self.THRESHOLDS["nation"]
            if fips == "00"
            else self.THRESHOLDS["county"]
        )
        return self.toposimplify(
            geojson.FeatureCollection(features), threshold
        )

    def handle(self, *args, **options):
        self.set_attributes()
        self.parse_arguments(options)

        state = Division.objects.get(code=15, level__name=DivisionLevel.STATE)

        geojson, created = Geometry.objects.update_or_create(
            division=state,
            subdivision_level=self.COUNTY_LEVEL,
            simplification=0.075,
            source="https://www2.census.gov/geo/tiger/GENZ2016/shp/cb_2016_us_state_500k.zip",  # noqa
            series="2016",
            defaults={"topojson": self.get_county_shp("15")},
        )

        # TODO: District geometries

        self.stdout.write(self.style.SUCCESS("All done! 🏁"))
