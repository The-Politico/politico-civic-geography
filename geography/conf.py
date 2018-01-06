"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

from django.conf import settings as project_settings


class Settings:
    pass


Settings.CENSUS_API_KEY = getattr(
    project_settings, 'CENSUS_API_KEY', None)

Settings.AWS_ACCESS_KEY_ID = getattr(
    project_settings, 'GEOGRAPHY_AWS_ACCESS_KEY_ID', None)

Settings.AWS_SECRET_ACCESS_KEY = getattr(
    project_settings, 'GEOGRAPHY_AWS_SECRET_ACCESS_KEY', None)

Settings.AWS_REGION = getattr(
    project_settings, 'GEOGRAPHY_AWS_REGION', 'us-east-1')

Settings.AWS_S3_BUCKET = getattr(
    project_settings, 'GEOGRAPHY_AWS_S3_BUCKET', None)

Settings.AWS_S3_UPLOAD_ROOT = getattr(
    project_settings,
    'GEOGRAPHY_AWS_S3_UPLOAD_ROOT',
    'elections')

Settings.AWS_ACL = getattr(
    project_settings, 'GEOGRAPHY_AWS_ACL', 'public-read')

Settings.AWS_CACHE_HEADER = getattr(
    project_settings, 'GEOGRAPHY_AWS_CACHE_HEADER', 'max-age=31536000')

Settings.API_AUTHENTICATION_CLASS = getattr(
    project_settings,
    'GEOGRAPHY_API_AUTHENTICATION_CLASS',
    'rest_framework.authentication.BasicAuthentication'
)

Settings.API_PERMISSION_CLASS = getattr(
    project_settings,
    'GEOGRAPHY_API_PERMISSION_CLASS',
    'rest_framework.permissions.IsAdminUser'
)

Settings.API_PAGINATION_CLASS = getattr(
    project_settings,
    'GEOGRAPHY_API_PAGINATION_CLASS',
    'geography.pagination.ResultsPagination'
)

settings = Settings
