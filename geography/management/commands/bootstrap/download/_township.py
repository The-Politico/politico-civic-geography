import os
import shutil
import urllib.request as request
import zipfile
from pathlib import Path

import us
from geography.utils.lookups import township_states

SHP_BASE = 'https://www2.census.gov/geo/tiger/GENZ{}/shp/'
DATA_DIRECTORY = './tmp/data/geography/'


class DownloadTownship(object):
    def download_township_data(self):
        for state in township_states:
            state_fips = us.states.lookup(state).fips
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
