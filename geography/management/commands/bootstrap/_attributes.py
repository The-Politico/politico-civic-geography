# Imports from other dependencies.
from tqdm._utils import _term_move_up


# Imports from geography.
from geography.models import Division
from geography.models import DivisionLevel


class Attributes(object):
    def set_attributes(self):
        self.NATIONAL_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.COUNTRY
        )
        self.STATE_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.STATE, parent=self.NATIONAL_LEVEL
        )
        self.DISTRICT_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.DISTRICT, parent=self.STATE_LEVEL
        )
        self.COUNTY_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.COUNTY, parent=self.STATE_LEVEL
        )

        # Other fixtures
        self.TOWNSHIP_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.TOWNSHIP, parent=self.COUNTY_LEVEL
        )
        self.PRECINCT_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.PRECINCT, parent=self.COUNTY_LEVEL
        )
        self.VOTERS_ABROAD_LEVEL, created = DivisionLevel.objects.get_or_create(
            name=DivisionLevel.VOTERS_ABROAD
        )

        self.NATION, created = Division.objects.get_or_create(
            code="00",
            name="United States of America",
            label="United States of America",
            short_label="USA",
            level=self.NATIONAL_LEVEL,
        )

        self.TQDM_PREFIX = _term_move_up() + "\r"
        self.SHP_SOURCE_BASE = "https://www2.census.gov/geo/tiger/GENZ{}/shp/"
        self.DOWNLOAD_DIRECTORY = "./tmp/data/geography/"
