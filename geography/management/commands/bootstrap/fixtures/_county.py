# Imports from other dependencies.
from tqdm import tqdm


# Imports from geography.
from geography.models import Division
from geography.utils.lookups import counties


class CountyFixtures(object):
    def create_county_fixtures(self):
        for county in tqdm(counties, desc="Counties"):
            # Skip territories and DC
            if int(county["state"]) > 56 or int(county["state"]) == 11:
                continue
            state = Division.objects.get(
                code=county["state"], level=self.STATE_LEVEL
            )
            Division.objects.update_or_create(
                level=self.COUNTY_LEVEL,
                code="{}{}".format(county["state"], county["county"]),
                parent=state,
                defaults={
                    "name": county["NAME"],
                    "label": county["NAME"],
                    "code_components": {
                        "fips": {
                            "state": county["state"],
                            "county": county["county"],
                        }
                    },
                },
            )
            tqdm.write(
                self.TQDM_PREFIX
                + ">  FIPS {}{}     ".format(county["state"], county["county"])
            )
        tqdm.write(self.style.SUCCESS("Done.\n"))
