from tqdm import tqdm
from tqdm._utils import _term_move_up

from geography.models import Division
from geography.utils.lookups import counties

tqdm_prefix = _term_move_up() + '\r'
SHP_BASE = 'https://www2.census.gov/geo/tiger/GENZ{}/shp/'
DATA_DIRECTORY = './tmp/data/geography/'


class CountyFixtures(object):
    def create_county_fixtures(self):
        for county in tqdm(counties, desc='Counties'):
            if int(county['state']) > 56:
                continue
            state = Division.objects.get(
                code=county['state'],
                level=self.STATE_LEVEL
            )
            Division.objects.update_or_create(
                level=self.COUNTY_LEVEL,
                code='{}{}'.format(
                    county['state'],
                    county['county']
                ),
                parent=state,
                defaults={
                    'name': county['NAME'],
                    'label': county['NAME'],
                    'code_components': {
                        'fips': {
                            'state': county['state'],
                            'county': county['county']
                        }
                    }
                }
            )
            tqdm.write(tqdm_prefix + '>  FIPS {}{}     '.format(
                county['state'],
                county['county'],
            ))
        tqdm.write(self.style.SUCCESS('Done.\n'))
