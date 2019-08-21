# Imports from python.
import os


# Imports from other dependencies.
import geojson
import shapefile


# Imports from geography.
from geography.utils.lookups import township_lookup


class StateTownshipShapes(object):
    def get_state_township_shps(self, fips):
        SHP_SLUG = "cb_{}_{}_cousub_500k".format(self.YEAR, fips)
        DOWNLOAD_PATH = os.path.join(self.DOWNLOAD_DIRECTORY, SHP_SLUG)
        shape = shapefile.Reader(
            os.path.join(DOWNLOAD_PATH, "{}.shp".format(SHP_SLUG))
        )
        fields = shape.fields[1:]
        field_names = [f[0] for f in fields]
        township_records = [
            shp
            for shp in shape.shapeRecords()
            if dict(zip(field_names, shp.record))["STATEFP"] == fips
            or (
                fips == "00"
                and int(dict(zip(field_names, shp.record))["STATEFP"]) <= 56
            )
        ]
        features = []
        for shp in township_records:
            rec = dict(zip(field_names, shp.record))
            if rec["COUSUBFP"] == "00000":
                continue

            geometry = shp.shape.__geo_interface__
            geodata = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "state": rec["STATEFP"],
                    "county": rec["COUNTYFP"],
                    "countysub": rec["COUSUBFP"],
                    "name": township_lookup[rec["STATEFP"]][
                        rec["COUNTYFP"]
                    ].get(rec["COUSUBFP"], rec["NAME"]),
                },
            }
            features.append(geodata)
        threshold = self.THRESHOLDS["county"]
        return self.toposimplify(
            geojson.FeatureCollection(features), threshold
        )
