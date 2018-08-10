import os

import geojson
import shapefile
from django.contrib.humanize.templatetags.humanize import ordinal

DATA_DIRECTORY = './tmp/data/geography/'


class DistrictShape(object):
    def get_district_shp(self, fips):
        SHP_SLUG = 'cb_{}_us_cd{}_500k'.format(self.YEAR, self.CONGRESS)
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
        district_records = [
            shp for shp in shape.shapeRecords()
            if dict(zip(field_names, shp.record))['STATEFP'] == fips
        ]
        features = []
        for shp in district_records:
            rec = dict(zip(field_names, shp.record))
            code_key = 'CD{}FP'.format(self.CONGRESS)
            if int(rec[code_key]) == 0:
                label = 'At-large congressional district'.format(
                    ordinal(int(rec[code_key]))
                )
            else:
                label = '{} congressional district'.format(
                    ordinal(int(rec[code_key]))
                )

            geometry = shp.shape.__geo_interface__
            geodata = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'state': rec['STATEFP'],
                    'district': rec[code_key],
                    'name': label
                }
            }
            features.append(geodata)
        threshold = self.THRESHOLDS['district']
        return self.toposimplify(
            geojson.FeatureCollection(features),
            threshold
        )
