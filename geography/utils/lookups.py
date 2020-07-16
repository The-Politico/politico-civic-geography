# Imports from other dependencies.
from census import Census
from DictObject import DictObject
import us
from tqdm import tqdm

# Imports from geography.
from geography.conf import settings


tqdm.write("📌  Loading U.S. Census geo lookups...")

census = Census(settings.CENSUS_API_KEY)

############
# COUNTIES
tqdm.write("   County lookups")
counties = census.sf1.get("NAME", geo={"for": "county:*"})
county_lookup = DictObject({})


for county in tqdm(counties):
    c = DictObject(county)
    if c.state not in county_lookup:
        county_lookup[c.state] = {}
    county_lookup[c.state][c.county] = c.NAME

#############
# TOWNSHIPS
tqdm.write("   State township lookups")
townships = []
township_states = ["CT", "MA", "ME", "NH", "RI", "VT"]
township_lookup = DictObject({})
for state in tqdm(township_states):
    state_codes = us.states.lookup(state)

    state_townships = census.sf1.get(
        "NAME",
        geo={
            "for": "county subdivision:*",
            "in": "state:{} county:*".format(state_codes.fips),
        },
    )
    townships.extend(state_townships)
for township in townships:
    t = DictObject(township)
    if t.state not in township_lookup:
        township_lookup[t.state] = {}

    if t.county not in township_lookup[t.state]:
        township_lookup[t.state][t.county] = {}

    township_lookup[t.state][t.county][t.county_subdivision] = t.NAME
