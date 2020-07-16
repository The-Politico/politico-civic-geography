# Imports from python.
import os
from pathlib import Path
import shutil
import urllib.request as request
import zipfile


class DownloadState(object):
    def download_state_data(self):
        SHP_SLUG = "cb_{}_us_state_500k".format(self.YEAR)
        DOWNLOAD_PATH = os.path.join(self.DOWNLOAD_DIRECTORY, SHP_SLUG)
        ZIPFILE = "{}{}.zip".format(DOWNLOAD_PATH, SHP_SLUG)
        SHP_PATH = os.path.join(
            self.SHP_SOURCE_BASE.format(self.YEAR), SHP_SLUG
        )

        if not os.path.exists(DOWNLOAD_PATH):
            os.makedirs(DOWNLOAD_PATH)

        if not Path(ZIPFILE).is_file():
            with request.urlopen("{}.zip".format(SHP_PATH)) as response, open(
                ZIPFILE, "wb"
            ) as out_file:
                shutil.copyfileobj(response, out_file)

        if not Path("{}{}.shp".format(DOWNLOAD_PATH, SHP_SLUG)).is_file():
            with zipfile.ZipFile(ZIPFILE, "r") as file:
                file.extractall(DOWNLOAD_PATH)
