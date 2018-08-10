import json
import os

from tqdm import tqdm
from tqdm._utils import _term_move_up

import geojson
import shapefile
from geography.models import Geometry

tqdm_prefix = _term_move_up() + '\r'
SHP_BASE = 'https://www2.census.gov/geo/tiger/GENZ{}/shp/'
DATA_DIRECTORY = './tmp/data/geography/'


class NationFixtures(object):
    def create_nation_fixtures(self):
        """
        Create national US and State Map
        """
        SHP_SLUG = 'cb_{}_us_state_500k'.format(self.YEAR)
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
        features = []
        for shp in shape.shapeRecords():
            state = dict(zip(field_names, shp.record))
            geodata = {
                'type': 'Feature',
                'geometry': shp.shape.__geo_interface__,
                'properties': {
                    'state': state['STATEFP'],
                    'name': state['NAME']
                }
            }
            features.append(geodata)
        Geometry.objects.update_or_create(
            division=self.NATION,
            subdivision_level=self.STATE_LEVEL,
            simplification=self.THRESHOLDS['nation'],
            source=os.path.join(SHP_BASE.format(self.YEAR), SHP_SLUG) + '.zip',
            series=self.YEAR,
            defaults={
                'topojson': self.toposimplify(
                    geojson.FeatureCollection(features),
                    self.THRESHOLDS['nation']
                ),
            },
        )

        geo, created = Geometry.objects.update_or_create(
            division=self.NATION,
            subdivision_level=self.COUNTY_LEVEL,
            simplification=self.THRESHOLDS['nation'],
            source=os.path.join(SHP_BASE.format(self.YEAR), SHP_SLUG) + '.zip',
            series=self.YEAR,
            defaults={
                'topojson': self.get_county_shp('00'),
            },
        )
        tqdm.write('Nation\n')
        tqdm.write(tqdm_prefix + '>  FIPS {}  @ ~{}kb     '.format(
            '00',
            round(len(json.dumps(geo.topojson)) / 1000)
        ))
        tqdm.write(self.style.SUCCESS('Done.\n'))
