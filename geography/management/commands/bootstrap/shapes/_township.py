import os

import geojson
import shapefile
from geography.utils.lookups import township_lookup

DATA_DIRECTORY = './tmp/data/geography/'


class TownshipShape(object):
    def get_township_shp(self, fips):
        SHP_SLUG = 'cb_2017_{}_cousub_500k'.format(fips)
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
        township_records = [
            shp for shp in shape.shapeRecords()
            if dict(zip(field_names, shp.record))['STATEFP'] == fips or
            (
                fips == '00' and
                int(dict(zip(field_names, shp.record))['STATEFP']) <= 56
            )
        ]
        features = []
        for shp in township_records:
            rec = dict(zip(field_names, shp.record))
            if rec['COUSUBFP'] == '00000':
                continue

            geometry = shp.shape.__geo_interface__
            geodata = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'state': rec['STATEFP'],
                    'county': rec['COUNTYFP'],
                    'countysub': rec['COUSUBFP'],
                    'name': township_lookup[rec['STATEFP']][rec['COUNTYFP']].get( # noqa
                        rec['COUSUBFP'], rec['NAME']
                    )
                }
            }
            features.append(geodata)
        threshold = self.THRESHOLDS['county']
        return self.toposimplify(
            geojson.FeatureCollection(features),
            threshold
        )
