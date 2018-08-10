import os
import shutil
import urllib.request as request
import zipfile
from pathlib import Path

SHP_BASE = 'https://www2.census.gov/geo/tiger/GENZ{}/shp/'
DATA_DIRECTORY = './tmp/data/geography/'


class DownloadDistrict(object):
    def download_district_data(self):
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