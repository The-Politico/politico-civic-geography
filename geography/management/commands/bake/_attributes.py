# Imports from python.
import os


# Imports from other dependencies.
import boto3


# Imports from geography.
from geography.conf import settings
from geography.models import DivisionLevel


def get_bucket():
    session = boto3.session.Session(
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    s3 = session.resource("s3")
    return s3.Bucket(settings.AWS_S3_BUCKET)


class Attributes(object):
    def set_attributes(self):
        self.STATE_LEVEL = DivisionLevel.objects.get(name=DivisionLevel.STATE)
        self.DISTRICT_LEVEL = DivisionLevel.objects.get(
            name=DivisionLevel.DISTRICT
        )

        self.BUCKET = get_bucket()
        self.OUTPUT_PATH = os.path.join(
            settings.AWS_S3_UPLOAD_ROOT, "geography/us-census/cb/500k"
        )
