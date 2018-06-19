import json
import os
import shutil
import subprocess
import urllib.request as request
import zipfile
from pathlib import Path

import geojson
import shapefile
import us
from census import Census
from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.management.base import BaseCommand, CommandError
from geography.conf import settings
from geography.models import Division, DivisionLevel, Geometry
from tqdm import tqdm
from tqdm._utils import _term_move_up

tqdm_prefix = _term_move_up() + '\r'

SHP_BASE = 'https://www2.census.gov/geo/tiger/GENZ{}/shp/'
DATA_DIRECTORY = './tmp/data/geography/'

census = Census(settings.CENSUS_API_KEY)

COUNTIES = census.sf1.get('NAME', geo={'for': 'county:*'})
COUNTY_LOOKUP = {}
for c in COUNTIES:
    if c['state'] not in COUNTY_LOOKUP:
        COUNTY_LOOKUP[c['state']] = {}
    COUNTY_LOOKUP[c['state']][c['county']] = c['NAME']

TOWNSHIPS = []
TOWNSHIP_STATES = ['CT', 'MA', 'ME', 'NH', 'RI', 'VT']
TOWNSHIP_LOOKUP = {}
for state in TOWNSHIP_STATES:
    state_codes = us.states.lookup(state)

    for county_fips, name in COUNTY_LOOKUP[state_codes.fips].items():
        state_townships = census.sf1.get('NAME', geo={
            'for': 'county subdivision:*',
            'in': 'state:{} county:{}'.format(state_codes.fips, county_fips)
        })
        TOWNSHIPS.extend(state_townships)
        for t in state_townships:
            if t['state'] not in TOWNSHIP_LOOKUP:
                TOWNSHIP_LOOKUP[t['state']] = {}

            if t['county'] not in TOWNSHIP_LOOKUP[t['state']]:
                TOWNSHIP_LOOKUP[t['state']][t['county']] = {}

            TOWNSHIP_LOOKUP[t['state']][t['county']][t['county subdivision']] = t['NAME'] # noqa


class Command(BaseCommand):
    help = (
        'Downloads and bootstraps geographic data for states and counties '
        'from the U.S. Census Bureau simplified cartographic boundary files.'
    )

    def get_required_fixtures(self):
        self.NATIONAL_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.COUNTRY
        )
        self.STATE_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.STATE,
            parent=self.NATIONAL_LEVEL
        )
        self.DISTRICT_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.DISTRICT,
            parent=self.STATE_LEVEL
        )
        self.COUNTY_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.COUNTY,
            parent=self.STATE_LEVEL
        )

        # Other fixtures
        self.TOWNSHIP_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.TOWNSHIP,
            parent=self.COUNTY_LEVEL
        )
        DivisionLevel.objects.get_or_create(
            name=DivisionLevel.PRECINCT,
            parent=self.COUNTY_LEVEL
        )

        self.NATION, created = Division.objects.get_or_create(
            code='00',
            name='United States of America',
            label='United States of America',
            short_label='USA',
            level=self.NATIONAL_LEVEL,
        )

    def download_shp_data(self, geo):
        SHP_SLUG = 'cb_{}_us_{}_500k'.format(self.YEAR, geo.lower())
        DOWNLOAD_PATH = os.path.join(
            DATA_DIRECTORY,
            SHP_SLUG
        )
        ZIPFILE = '{}{}.zip'.format(DOWNLOAD_PATH, SHP_SLUG)
        SHP_PATH = os.path.join(
            SHP_BASE.format(self.YEAR),
            SHP_SLUG
        )

        if not os.path.exists(DOWNLOAD_PATH):
            os.makedirs(DOWNLOAD_PATH)

        if not Path(ZIPFILE).is_file():
            with request.urlopen('{}.zip'.format(SHP_PATH)) as response,\
                    open(ZIPFILE, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

        if not Path('{}{}.shp'.format(DOWNLOAD_PATH, SHP_SLUG)).is_file():
            with zipfile.ZipFile(ZIPFILE, 'r') as file:
                file.extractall(DOWNLOAD_PATH)

    def download_district_data(self):
        SHP_SLUG = 'cb_{}_us_cd{}_500k'.format(self.YEAR, self.CONGRESS)
        DOWNLOAD_PATH = os.path.join(
            DATA_DIRECTORY,
            SHP_SLUG
        )
        ZIPFILE = '{}{}.zip'.format(DOWNLOAD_PATH, SHP_SLUG)
        SHP_PATH = os.path.join(
            SHP_BASE.format(self.YEAR),
            SHP_SLUG
        )
        if not Path(ZIPFILE).is_file():
            with request.urlopen('{}.zip'.format(SHP_PATH)) as response,\
                    open(ZIPFILE, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

        if not Path('{}{}.shp'.format(DOWNLOAD_PATH, SHP_SLUG)).is_file():
            with zipfile.ZipFile(ZIPFILE, 'r') as file:
                file.extractall(DOWNLOAD_PATH)

    def download_township_data(self, state_fips):
        SHP_SLUG = 'cb_2017_{}_cousub_500k'.format(state_fips)
        DOWNLOAD_PATH = os.path.join(
            DATA_DIRECTORY,
            SHP_SLUG
        )
        ZIPFILE = '{}{}.zip'.format(DOWNLOAD_PATH, SHP_SLUG)
        SHP_PATH = os.path.join(
            SHP_BASE.format('2017'),
            SHP_SLUG
        )
        if not Path(ZIPFILE).is_file():
            with request.urlopen('{}.zip'.format(SHP_PATH)) as response,\
                    open(ZIPFILE, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

        if not Path('{}{}.shp'.format(DOWNLOAD_PATH, SHP_SLUG)).is_file():
            with zipfile.ZipFile(ZIPFILE, 'r') as file:
                file.extractall(DOWNLOAD_PATH)

    @staticmethod
    def toposimplify(geojson, p):
        """
        Convert geojson and simplify topology.

        geojson is a dict representing geojson.
        p is a simplification threshold value between 0 and 1.
        """
        proc_out = subprocess.run(
            ['geo2topo'],
            input=bytes(
                json.dumps(geojson),
                'utf-8'),
            stdout=subprocess.PIPE
        )
        proc_out = subprocess.run(
            ['toposimplify', '-P', p],
            input=proc_out.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        topojson = json.loads(proc_out.stdout)
        # Standardize object name
        topojson['objects']['divisions'] = topojson['objects'].pop('-')
        return topojson

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
                    'name': COUNTY_LOOKUP[rec['STATEFP']].get(
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
                    'name': TOWNSHIP_LOOKUP[rec['STATEFP']][rec['COUNTYFP']].get(
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

    def create_state_fixtures(self):
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

        nation_obj = Division.objects.get(code='00', level=self.NATIONAL_LEVEL)

        for shp in tqdm(shape.shapeRecords(), desc='States'):
            state = dict(zip(field_names, shp.record))
            postal = us.states.lookup(state['STATEFP']).abbr
            # Skip territories
            if int(state['STATEFP']) > 56:
                continue
            state_obj, created = Division.objects.update_or_create(
                code=state['STATEFP'],
                level=self.STATE_LEVEL,
                parent=nation_obj,
                defaults={
                    'name': state['NAME'],
                    'label': state['NAME'],
                    'code_components': {
                        'fips': {
                            'state': state['STATEFP'],
                        },
                        'postal': postal,
                    },
                }
            )
            geodata = {
                'type': 'Feature',
                'geometry': shp.shape.__geo_interface__,
                'properties': {
                    'state': state['STATEFP'],
                    'name': state['NAME']
                }
            }
            geojson, created = Geometry.objects.update_or_create(
                division=state_obj,
                subdivision_level=self.STATE_LEVEL,
                simplification=self.THRESHOLDS['state'],
                source=os.path.join(
                    SHP_BASE.format(self.YEAR), SHP_SLUG) + '.zip',
                series=self.YEAR,
                defaults={
                    'topojson': self.toposimplify(
                        geodata,
                        self.THRESHOLDS['state']
                    ),
                },
            )
            geojson, created = Geometry.objects.update_or_create(
                division=state_obj,
                subdivision_level=self.COUNTY_LEVEL,
                simplification=self.THRESHOLDS['county'],
                source=os.path.join(
                    SHP_BASE.format(self.YEAR), SHP_SLUG) + '.zip',
                series=self.YEAR,
                defaults={
                    'topojson': self.get_county_shp(state['STATEFP']),
                },
            )
            geojson, created = Geometry.objects.update_or_create(
                division=state_obj,
                subdivision_level=self.DISTRICT_LEVEL,
                simplification=self.THRESHOLDS['district'],
                source=os.path.join(
                    SHP_BASE.format(self.YEAR),
                    'cb_{}_us_cd{}_500k'.format(self.YEAR, self.CONGRESS)
                ) + '.zip',
                series=self.YEAR,
                defaults={
                    'topojson': self.get_district_shp(state['STATEFP']),
                },
            )

            if postal in TOWNSHIP_STATES:
                geojson, created = Geometry.objects.update_or_create(
                    division=state_obj,
                    subdivision_level=self.TOWNSHIP_LEVEL,
                    simplification=self.THRESHOLDS['county'],
                    source=os.path.join(
                        SHP_BASE.format(self.YEAR),
                        'cb_2017_{}_cousub_500k'.format(state['STATEFP'])
                    ) + '.zip',
                    series=self.YEAR,
                    defaults={
                        'topojson': self.get_township_shp(state['STATEFP']),
                    },
                )

            tqdm.write(tqdm_prefix + '>  FIPS {}  @ ~{}kb     '.format(
                state['STATEFP'],
                round(len(json.dumps(geojson.topojson)) / 1000)
            ))
        tqdm.write(self.style.SUCCESS('Done.\n'))

    def create_district_fixtures(self):
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

        for shp in tqdm(shape.shapeRecords(), desc='Districts'):
            district = dict(zip(field_names, shp.record))

            if int(district['STATEFP']) > 56:
                continue

            state = Division.objects.get(
                code=district['STATEFP'],
                level=self.STATE_LEVEL
            )
            code_key = 'CD{}FP'.format(self.CONGRESS)
            if int(district[code_key]) == 0:
                label = '{} at-large congressional district'.format(
                    state.label,
                    ordinal(int(district[code_key]))
                )
            else:
                label = '{} {} congressional district'.format(
                    state.label,
                    ordinal(int(district[code_key]))
                )
            district_obj, created = Division.objects.update_or_create(
                code=district[code_key],
                level=self.DISTRICT_LEVEL,
                parent=state,
                defaults={
                    'name': label,
                    'label': label,
                    'code_components': {
                        'fips': {
                            'state': state.code,
                        },
                        'district': district[code_key]
                    },
                }
            )
            geodata = {
                'type': 'Feature',
                'geometry': shp.shape.__geo_interface__,
                'properties': {
                    'state': state.code,
                    'district': district[code_key],
                    'name': label
                }
            }
            geojson, created = Geometry.objects.update_or_create(
                division=district_obj,
                subdivision_level=self.DISTRICT_LEVEL,
                simplification=self.THRESHOLDS['district'],
                source=os.path.join(
                    SHP_BASE.format(self.YEAR), SHP_SLUG) + '.zip',
                series=self.YEAR,
                defaults={
                    'topojson': self.toposimplify(
                        geodata,
                        self.THRESHOLDS['district']
                    ),
                },
            )
            tqdm.write(
                tqdm_prefix + '>  FIPS {}, District {}  @ ~{}kb     '.format(
                    district['STATEFP'],
                    district[code_key],
                    round(len(json.dumps(geojson.topojson)) / 1000)
                )
            )
        tqdm.write(self.style.SUCCESS('Done.\n'))

    def create_county_fixtures(self):
        for county in tqdm(COUNTIES, desc='Counties'):
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

    def create_township_fixtures(self):
        for township in tqdm(TOWNSHIPS, desc='Townships'):
            if township['county subdivision'] == '00000':
                continue

            if int(township['state']) > 56:
                continue
            county = Division.objects.get(
                code='{}{}'.format(township['state'], township['county']),
                level=self.COUNTY_LEVEL
            )
            Division.objects.update_or_create(
                level=self.TOWNSHIP_LEVEL,
                code='{}{}{}'.format(
                    township['state'],
                    township['county'],
                    township['county subdivision']
                ),
                parent=county,
                defaults={
                    'name': township['NAME'],
                    'label': township['NAME'],
                    'code_components': {
                        'fips': {
                            'state': township['state'],
                            'county': township['county'],
                            'subdivision': township['county subdivision']
                        }
                    }
                }
            )
            tqdm.write(tqdm_prefix + '>  FIPS {}{}{}     '.format(
                township['state'],
                township['county'],
                township['county subdivision']
            ))
        tqdm.write(self.style.SUCCESS('Done.\n'))

    def add_arguments(self, parser):
        def check_threshold(arg):
            value = float(arg)
            if value < 0 or value > 1:
                raise CommandError(
                    'Threshold must be a decimal between 0 and 1.'
                )
            return value

        parser.add_argument(
            '--year',
            action='store',
            dest='year',
            default='2016',
            help='Specify year of shapefile series (default, 2016)',
        )
        parser.add_argument(
            '--congress',
            action='store',
            dest='congress',
            default='115',
            help='Specify congress of district shapefile series \
             (default, 115)',
        )
        parser.add_argument(
            '--states',
            action='store_true',
            dest='states',
            help='Just load states',
        )
        parser.add_argument(
            '--counties',
            action='store_true',
            dest='counties',
            help='Just load counties',
        )
        parser.add_argument(
            '--districts',
            action='store_true',
            dest='districts',
            help='Just load districts',
        )
        parser.add_argument(
            '--townships',
            action='store_true',
            dest='townships',
            help='Just load townships',
        )
        parser.add_argument(
            '--nationThreshold',
            type=check_threshold,
            default=0.005,
            dest='nationThreshold',
            help='Simplification threshold value for nation topojson \
                (default, 0.005)'
        )
        parser.add_argument(
            '--stateThreshold',
            type=check_threshold,
            default=0.05,
            dest='stateThreshold',
            help='Simplification threshold value for state topojson \
                (default, 0.05)'
        )
        parser.add_argument(
            '--districtThreshold',
            type=check_threshold,
            default=0.08,
            dest='districtThreshold',
            help='Simplification threshold value for district topojson \
                (default, 0.08)'
        )
        parser.add_argument(
            '--countyThreshold',
            type=check_threshold,
            default=0.075,
            dest='countyThreshold',
            help='Simplification threshold value for county topojson \
                (default, 0.075)'
        )

    def handle(self, *args, **options):
        self.get_required_fixtures()
        self.YEAR = options['year']
        self.CONGRESS = options['congress']
        self.THRESHOLDS = {
            'nation': str(options['nationThreshold']),
            'state': str(options['stateThreshold']),
            'district': str(options['districtThreshold']),
            'county': str(options['countyThreshold']),
        }

        if options['counties'] and options['states']:
            raise CommandError('Can\'t load only counties and only states...')

        tqdm.write('Downloading data')
        self.download_shp_data('state')
        self.download_shp_data('county')
        self.download_district_data()
        for state in TOWNSHIP_STATES:
            fips = us.states.lookup(state).fips
            self.download_township_data(fips)

        tqdm.write('Creating fixtures')
        self.create_nation_fixtures()
        if (not options['counties'] and not options['districts']
                and not options['townships']):
            self.create_state_fixtures()
        if (not options['counties'] and not options['states']
                and not options['townships']):
            self.create_district_fixtures()
        if (not options['states'] and not options['districts']
                and not options['townships']):
            self.create_county_fixtures()
        if (not options['states'] and not options['counties']
                and not options['districts']):
            self.create_township_fixtures()

        self.stdout.write(
            self.style.SUCCESS('All done! 🏁')
        )
