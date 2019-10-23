# Imports from Django.
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UniqueIdentifierMixin
from civic_utils.models import UUIDMixin
from uuslug import slugify


class DivisionLevel(UniqueIdentifierMixin, UUIDMixin, CivicBaseModel):
    """Level of government or administration where a division exists.

    Exempli gratia, federal, state, district, county, precinct, municipal.
    """

    natural_key_fields = ["name"]
    uid_prefix = "divisionlevel"
    uid_base_field = "slug"
    # default_serializer = ""

    COUNTRY = "country"
    STATE = "state"
    DISTRICT = "district"
    COUNTY = "county"
    TOWNSHIP = "township"
    PRECINCT = "precinct"

    LEVEL_CHOICES = (
        (COUNTRY, "Country"),
        (STATE, "State"),
        (DISTRICT, "District"),
        (COUNTY, "County"),
        (TOWNSHIP, "Township"),
        (PRECINCT, "Precinct"),
    )

    name = models.CharField(max_length=255, unique=True, choices=LEVEL_CHOICES)

    slug = models.SlugField(
        blank=True, max_length=255, unique=True, editable=False
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        self.generate_unique_identifier()

        super(DivisionLevel, self).save(*args, **kwargs)

    def get_uid_prefix(self):
        if self.parent:
            return "{}:{}".format(self.parent.uid, self.uid)

        return self.uid
