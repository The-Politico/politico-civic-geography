import json
import os

import boto3
from django.core.management.base import BaseCommand
from geography.conf import settings
from geography.models import Division, DivisionLevel, Geometry
from tqdm import tqdm

OUTPUT_PATH = os.path.join(
    settings.AWS_S3_UPLOAD_ROOT,
    'geography/us-census/cb/500k'
)


def get_bucket():
    session = boto3.session.Session(
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    s3 = session.resource('s3')
    return s3.Bucket(settings.AWS_S3_BUCKET)


class Command(BaseCommand):
    help = 'Uploads topojson by state.'

    def add_arguments(self, parser):
        parser.add_argument(
            'states',
            nargs='+',
            help="States to export by FIPS code. \
            Use 00 to export all geographies."
        )

        parser.add_argument(
            '--year',
            action='store',
            dest='year',
            default='2016',
            help='Specify year of shapefile series (default, 2016)',
        )

    def handle(self, *args, **options):
        print('Exporting geographies')

        states = options['states']
        year = options['year']
        bucket = get_bucket()

        STATE_LEVEL = DivisionLevel.objects.get(name=DivisionLevel.STATE)
        geometries = None
        if states[0] == '00':
            geometries = Geometry.objects.filter(
                series=year, division__level=STATE_LEVEL)
        else:
            for state in states:
                division = Division.objects.get(level=STATE_LEVEL, code=state)
                if not geometries:
                    geometries = division.geometries.filter(series=year)
                else:
                    geometries = geometries | division.geometries.filter(
                        series=year
                    )

        for geometry in tqdm(geometries):
            key = os.path.join(
                OUTPUT_PATH,
                options['year'],
                'states',
                geometry.division.code,
                '{}.json'.format(geometry.subdivision_level.slug)
            )
            bucket.put_object(
                Key=key,
                ACL=settings.AWS_ACL,
                Body=json.dumps(geometry.topojson),
                CacheControl=settings.AWS_CACHE_HEADER,
                ContentType='application/json'
            )
