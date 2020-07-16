# Imports from python.
import os


# Imports from other dependencies.
import geojson
import shapefile
from shapely.geometry import mapping
from shapely.geometry import shape


# Imports from geography.
from geography.utils.lookups import county_lookup


class DistrictCountyShapes(object):
    def get_district_county_shps(self, fips, district_code):
        DISTRICT_SHP_SLUG = "cb_{}_us_cd{}_500k".format(
            self.YEAR, self.CONGRESS
        )
        DISTRICT_SHP_PATH = os.path.join(
            self.DOWNLOAD_DIRECTORY, DISTRICT_SHP_SLUG
        )
        district_shape = shapefile.Reader(
            os.path.join(DISTRICT_SHP_PATH, "{}.shp".format(DISTRICT_SHP_SLUG))
        )
        district_fields = district_shape.fields[1:]
        district_field_names = [f[0] for f in district_fields]
        district_code_key = "CD{}FP".format(self.CONGRESS)
        district_record = [
            shp
            for shp in district_shape.shapeRecords()
            if dict(zip(district_field_names, shp.record))["STATEFP"] == fips
            and dict(zip(district_field_names, shp.record))[district_code_key]
            == district_code
        ][0]
        district_shapely = shape(district_record.shape.__geo_interface__)

        COUNTY_SHP_SLUG = "cb_{}_us_county_500k".format(self.YEAR)
        COUNTY_SHP_PATH = os.path.join(
            self.DOWNLOAD_DIRECTORY, COUNTY_SHP_SLUG
        )

        county_shape = shapefile.Reader(
            os.path.join(COUNTY_SHP_PATH, "{}.shp".format(COUNTY_SHP_SLUG))
        )
        county_fields = county_shape.fields[1:]
        county_field_names = [f[0] for f in county_fields]
        county_records = [
            shp
            for shp in county_shape.shapeRecords()
            if dict(zip(county_field_names, shp.record))["STATEFP"] == fips
            and shape(shp.shape.__geo_interface__).intersects(district_shapely)
        ]
        features = []
        for shp in county_records:
            intersection = shape(shp.shape.__geo_interface__).intersection(
                district_shapely
            )
            rec = dict(zip(county_field_names, shp.record))
            geodata = {
                "type": "Feature",
                "geometry": mapping(intersection),
                "properties": {
                    "state": rec["STATEFP"],
                    "district": district_code,
                    "county": rec["COUNTYFP"],
                    "name": county_lookup[rec["STATEFP"]].get(
                        rec["COUNTYFP"], rec["NAME"]
                    ),
                },
            }
            features.append(geodata)
        return self.toposimplify(
            geojson.FeatureCollection(features), self.THRESHOLDS["county"]
        )
