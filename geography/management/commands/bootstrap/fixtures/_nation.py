# Imports from python.
import json
import os


# Imports from other dependencies.
import geojson
import shapefile
from tqdm import tqdm
from uuslug import slugify


# Imports from geography.
from geography.models import Geometry


class NationFixtures(object):
    def create_nation_fixtures(self):
        """
        Create national US and State Map
        """
        SHP_SLUG = "cb_{}_us_state_500k".format(self.YEAR)
        DOWNLOAD_PATH = os.path.join(self.DOWNLOAD_DIRECTORY, SHP_SLUG)

        shape = shapefile.Reader(
            os.path.join(DOWNLOAD_PATH, "{}.shp".format(SHP_SLUG))
        )
        fields = shape.fields[1:]
        field_names = [f[0] for f in fields]
        features = []
        for shp in shape.shapeRecords():
            state = dict(zip(field_names, shp.record))
            geodata = {
                "type": "Feature",
                "geometry": shp.shape.__geo_interface__,
                "properties": {
                    "state": state["STATEFP"],
                    "name": state["NAME"],
                },
            }
            features.append(geodata)
        Geometry.objects.update_or_create(
            division=self.NATION,
            subdivision_level=self.STATE_LEVEL,
            simplification=self.THRESHOLDS["nation"],
            data_summary=slugify(
                "{}--{}--{}".format(
                    self.NATION.slug,
                    self.STATE_LEVEL.slug,
                    self.THRESHOLDS["nation"],
                )
            ),
            source=os.path.join(
                self.SHP_SOURCE_BASE.format(self.YEAR), SHP_SLUG
            )
            + ".zip",
            series=self.YEAR,
            defaults={
                "topojson": self.toposimplify(
                    geojson.FeatureCollection(features),
                    self.THRESHOLDS["nation"],
                )
            },
        )

        geo, created = Geometry.objects.update_or_create(
            division=self.NATION,
            subdivision_level=self.COUNTY_LEVEL,
            simplification=self.THRESHOLDS["nation"],
            data_summary=slugify(
                "{}--{}--{}".format(
                    self.NATION.slug,
                    self.COUNTY_LEVEL.slug,
                    self.THRESHOLDS["nation"],
                )
            ),
            source=os.path.join(
                self.SHP_SOURCE_BASE.format(self.YEAR), SHP_SLUG
            )
            + ".zip",
            series=self.YEAR,
            defaults={"topojson": self.get_state_county_shps("00")},
        )
        tqdm.write("Nation\n")
        tqdm.write(
            self.TQDM_PREFIX
            + ">  FIPS {}  @ ~{}kb     ".format(
                "00", round(len(json.dumps(geo.topojson)) / 1000)
            )
        )
        tqdm.write(self.style.SUCCESS("Done.\n"))
