# Imports from other dependencies.
from census import Census
from DictObject import DictObject
import us


# Imports from geography.
from geography.conf import settings


census = Census(settings.CENSUS_API_KEY)

############
# COUNTIES

counties = census.sf1.get("NAME", geo={"for": "county:*"})
county_lookup = DictObject({})

for county in counties:
    c = DictObject(county)
    if c.state not in county_lookup:
        county_lookup[c.state] = {}
    county_lookup[c.state][c.county] = c.NAME

#############
# TOWNSHIPS

townships = []
township_states = ["CT", "MA", "ME", "NH", "RI", "VT"]
township_lookup = DictObject({})

for state in township_states:
    state_codes = us.states.lookup(state)

    for county_fips, name in county_lookup[state_codes.fips].items():
        state_townships = census.sf1.get(
            "NAME",
            geo={
                "for": "county subdivision:*",
                "in": "state:{} county:{}".format(
                    state_codes.fips, county_fips
                ),
            },
        )
        townships.extend(state_townships)
        for township in state_townships:
            t = DictObject(township)
            if t.state not in township_lookup:
                township_lookup[t.state] = {}

            if t.county not in township_lookup[t.state]:
                township_lookup[t.state][t.county] = {}

            township_lookup[t.state][t.county][t.county_subdivision] = t.NAME
