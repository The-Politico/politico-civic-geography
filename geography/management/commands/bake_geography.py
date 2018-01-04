import json
import os

import boto3
from django.core.management.base import BaseCommand
from geography.conf import settings
from geography.models import Division, DivisionLevel, Geography
from tqdm import tqdm

OUTPUT_PATH = os.path.join(
    settings.AWS_S3_UPLOAD_ROOT,
    'data/geography'
)


def get_bucket():
    session = boto3.session.Session(
        region_name=settings.AWS_S3_REGION,
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
            Use * to export all geographies."
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

        geographies = None
        if states[0] == '*':
            geographies = Geography.objects.filter(
                series=year, division__level=STATE_LEVEL)
        else:
            for state in states:
                division = Division.objects.get(level=STATE_LEVEL, code=state)
                if not geographies:
                    geographies = division.geographies.filter(series=year)
                else:
                    geographies = geographies | division.geographies.filter(
                        series=year
                    )

        for geography in tqdm(geographies):
            key = os.path.join(
                OUTPUT_PATH,
                options['year'],
                'state',
                geography.division.code,
                '{}.json'.format(geography.subdivision_level.slug)
            )
            bucket.put_object(
                Key=key,
                ACL=settings.AWS_ACL,
                Body=json.dumps(geography.topojson),
                CacheControl=settings.AWS_CACHE_HEADER,
                ContentType='application/json'
            )
