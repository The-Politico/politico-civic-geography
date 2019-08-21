# Imports from python.
import os
from pathlib import Path
import shutil
import urllib.request as request
import zipfile


# Imports from other dependencies.
import us


# Imports from geography.
from geography.utils.lookups import township_states


class DownloadTownship(object):
    def download_township_data(self):
        for state in township_states:
            state_fips = us.states.lookup(state).fips
            SHP_SLUG = "cb_{}_{}_cousub_500k".format(self.YEAR, state_fips)
            DOWNLOAD_PATH = os.path.join(self.DOWNLOAD_DIRECTORY, SHP_SLUG)
            ZIPFILE = "{}{}.zip".format(DOWNLOAD_PATH, SHP_SLUG)
            SHP_PATH = os.path.join(
                self.SHP_SOURCE_BASE.format(self.YEAR), SHP_SLUG
            )
            if not Path(ZIPFILE).is_file():
                with request.urlopen(
                    "{}.zip".format(SHP_PATH)
                ) as response, open(ZIPFILE, "wb") as out_file:
                    shutil.copyfileobj(response, out_file)

            if not Path("{}{}.shp".format(DOWNLOAD_PATH, SHP_SLUG)).is_file():
                with zipfile.ZipFile(ZIPFILE, "r") as file:
                    file.extractall(DOWNLOAD_PATH)
