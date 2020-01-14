# Imports from python.
import json
import os


# Imports from other dependencies.
import shapefile
from tqdm import tqdm
import us
from uuslug import slugify


# Imports from geography.
from geography.models import Division
from geography.models import Geometry
from geography.utils.lookups import township_states


class StateFixtures(object):
    def create_state_fixtures(self):
        SHP_SLUG = "cb_{}_us_state_500k".format(self.YEAR)
        DOWNLOAD_PATH = os.path.join(self.DOWNLOAD_DIRECTORY, SHP_SLUG)

        shape = shapefile.Reader(
            os.path.join(DOWNLOAD_PATH, "{}.shp".format(SHP_SLUG))
        )
        fields = shape.fields[1:]
        field_names = [f[0] for f in fields]

        nation_obj = Division.objects.get(code="00", level=self.NATIONAL_LEVEL)

        for shp in tqdm(shape.shapeRecords(), desc="States"):
            state = dict(zip(field_names, shp.record))
            postal = us.states.lookup(state["STATEFP"]).abbr

            state_obj, created = Division.objects.update_or_create(
                code=state["STATEFP"],
                level=self.STATE_LEVEL,
                parent=nation_obj,
                defaults={
                    "name": state["NAME"],
                    "label": state["NAME"],
                    "code_components": {
                        "fips": {"state": state["STATEFP"]},
                        "postal": postal,
                    },
                },
            )
            geodata = {
                "type": "Feature",
                "geometry": shp.shape.__geo_interface__,
                "properties": {
                    "state": state["STATEFP"],
                    "name": state["NAME"],
                },
            }
            geojson, created = Geometry.objects.update_or_create(
                division=state_obj,
                subdivision_level=self.STATE_LEVEL,
                simplification=self.THRESHOLDS["state"],
                data_summary=slugify(
                    "{}--{}--{}".format(
                        state_obj.slug,
                        self.STATE_LEVEL.slug,
                        self.THRESHOLDS["state"],
                    )
                ),
                source=os.path.join(
                    self.SHP_SOURCE_BASE.format(self.YEAR), SHP_SLUG
                )
                + ".zip",
                series=self.YEAR,
                defaults={
                    "topojson": self.toposimplify(
                        geodata, self.THRESHOLDS["state"]
                    )
                },
            )
            geojson, created = Geometry.objects.update_or_create(
                division=state_obj,
                subdivision_level=self.COUNTY_LEVEL,
                simplification=self.THRESHOLDS["county"],
                data_summary=slugify(
                    "{}--{}--{}".format(
                        state_obj.slug,
                        self.COUNTY_LEVEL.slug,
                        self.THRESHOLDS["county"],
                    )
                ),
                source=os.path.join(
                    self.SHP_SOURCE_BASE.format(self.YEAR), SHP_SLUG
                )
                + ".zip",
                series=self.YEAR,
                defaults={
                    "topojson": self.get_state_county_shps(state["STATEFP"])
                },
            )
            geojson, created = Geometry.objects.update_or_create(
                division=state_obj,
                subdivision_level=self.DISTRICT_LEVEL,
                simplification=self.THRESHOLDS["district"],
                data_summary=slugify(
                    "{}--{}--{}".format(
                        state_obj.slug,
                        self.DISTRICT_LEVEL.slug,
                        self.THRESHOLDS["district"],
                    )
                ),
                source=os.path.join(
                    self.SHP_SOURCE_BASE.format(self.YEAR),
                    "cb_{}_us_cd{}_500k".format(self.YEAR, self.CONGRESS),
                )
                + ".zip",
                series=self.YEAR,
                defaults={
                    "topojson": self.get_state_district_shps(state["STATEFP"])
                },
            )

            if postal in township_states:
                geojson, created = Geometry.objects.update_or_create(
                    division=state_obj,
                    subdivision_level=self.TOWNSHIP_LEVEL,
                    simplification=self.THRESHOLDS["county"],
                    data_summary=slugify(
                        "{}--{}--{}".format(
                            state_obj.slug,
                            self.TOWNSHIP_LEVEL.slug,
                            self.THRESHOLDS["county"],
                        )
                    ),
                    source=os.path.join(
                        self.SHP_SOURCE_BASE.format(self.YEAR),
                        "cb_{}_{}_cousub_500k".format(
                            self.YEAR, state["STATEFP"]
                        ),
                    )
                    + ".zip",
                    series=self.YEAR,
                    defaults={
                        "topojson": self.get_state_township_shps(
                            state["STATEFP"]
                        )
                    },
                )

            tqdm.write(
                self.TQDM_PREFIX
                + ">  FIPS {}  @ ~{}kb     ".format(
                    state["STATEFP"],
                    round(len(json.dumps(geojson.topojson)) / 1000),
                )
            )
        tqdm.write(self.style.SUCCESS("Done.\n"))
