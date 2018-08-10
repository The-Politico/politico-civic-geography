import os

import geojson
import shapefile
from geography.utils.lookups import county_lookup

DATA_DIRECTORY = './tmp/data/geography/'


class CountyShape(object):
    def get_county_shp(self, fips):
        SHP_SLUG = 'cb_{}_us_county_500k'.format(self.YEAR)
        DOWNLOAD_PATH = os.path.join(
            DATA_DIRECTORY,
            SHP_SLUG
        )
        shape = shapefile.Reader(os.path.join(
            DOWNLOAD_PATH,
            '{}.shp'.format(SHP_SLUG)
        ))
        fields = shape.fields[1:]
        field_names = [f[0] for f in fields]
        county_records = [
            shp for shp in shape.shapeRecords()
            if dict(zip(field_names, shp.record))['STATEFP'] == fips or
            (
                fips == '00' and
                int(dict(zip(field_names, shp.record))['STATEFP']) <= 56
            )
        ]
        features = []
        for shp in county_records:
            rec = dict(zip(field_names, shp.record))
            geometry = shp.shape.__geo_interface__
            geodata = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'state': rec['STATEFP'],
                    'county': rec['COUNTYFP'],
                    'name': county_lookup[rec['STATEFP']].get(
                        rec['COUNTYFP'], rec['NAME']
                    )
                }
            }
            features.append(geodata)
        threshold = self.THRESHOLDS['nation'] if fips == '00' else \
            self.THRESHOLDS['county']
        return self.toposimplify(
            geojson.FeatureCollection(features),
            threshold
        )
