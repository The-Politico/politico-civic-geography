# Imports from python.
import os


# Imports from other dependencies.
from tqdm import tqdm


# Imports from geography.
from geography.conf import settings
from geography.models import Division
from geography.models import Geometry


class StateGeometries(object):
    def bake_state_geometries(self):
        state_geometries = None
        if self.STATES[0] == "00":
            state_geometries = Geometry.objects.filter(
                series=self.YEAR, division__level=self.STATE_LEVEL
            )
        else:
            for state in self.STATES:
                division = Division.objects.get(
                    level=self.STATE_LEVEL, code=state
                )
                if not state_geometries:
                    state_geometries = division.geometries.filter(
                        series=self.YEAR
                    )
                else:
                    state_geometries = (
                        state_geometries
                        | division.geometries.filter(series=self.YEAR)
                    )

        for geometry in tqdm(state_geometries, desc="State Geometries"):
            key = os.path.join(
                self.OUTPUT_PATH,
                self.YEAR,
                "states",
                geometry.division.code,
                "{0}-{1}.json".format(
                    geometry.division.code, geometry.subdivision_level.slug
                ),
            )
            self.BUCKET.put_object(
                Key=key,
                ACL=settings.AWS_ACL,
                Body=geometry.to_topojson(),
                CacheControl=settings.AWS_CACHE_HEADER,
                ContentType="application/json",
            )
        tqdm.write(self.style.SUCCESS("Done.\n"))
