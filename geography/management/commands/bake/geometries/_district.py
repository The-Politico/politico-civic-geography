# Imports from python.
import os


# Imports from other dependencies.
from tqdm import tqdm
import us


# Imports from geography.
from geography.conf import settings
from geography.models import Division
from geography.models import Geometry


class DistrictGeometries(object):
    def bake_district_geometries(self):
        district_geometries = None
        if self.STATES[0] == "00":
            district_geometries = Geometry.objects.filter(
                series=self.YEAR, division__level=self.DISTRICT_LEVEL
            )
        else:
            for state in self.STATES:
                division = Division.objects.get(
                    level=self.DISTRICT_LEVEL, parent__code=state
                )
                if not district_geometries:
                    district_geometries = division.geometries.filter(
                        series=self.YEAR
                    )
                else:
                    district_geometries = (
                        district_geometries
                        | division.geometries.filter(series=self.YEAR)
                    )

        for geometry in tqdm(district_geometries, desc="District Geometries"):
            state = us.states.lookup(geometry.division.parent.code)
            slug = "{}-{}".format(state.abbr, geometry.division.code)
            key = os.path.join(
                self.OUTPUT_PATH,
                self.YEAR,
                "districts",
                slug,
                "{0}.json".format(geometry.subdivision_level.slug),
            )
            self.BUCKET.put_object(
                Key=key,
                ACL=settings.AWS_ACL,
                Body=geometry.to_topojson(),
                CacheControl=settings.AWS_CACHE_HEADER,
                ContentType="application/json",
            )
        tqdm.write(self.style.SUCCESS("Done.\n"))
