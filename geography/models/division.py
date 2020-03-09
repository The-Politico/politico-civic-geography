# Imports from Django.
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import CommonIdentifiersMixin
from civic_utils.models import UUIDMixin


# Imports from geography.
from geography.models.division_level import DivisionLevel
from geography.models.intersect_relationship import IntersectRelationship


class Division(CommonIdentifiersMixin, UUIDMixin, CivicBaseModel):
    """A political or administrative geography.

    For example, a certain state, county, district, precinct or municipality.
    """

    natural_key_fields = ["level", "uid"]
    uid_prefix = "division"
    uid_base_field = "name"
    # default_serializer = ""

    name = models.CharField(max_length=255)

    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    level = models.ForeignKey(
        DivisionLevel, on_delete=models.PROTECT, related_name="divisions"
    )

    code = models.CharField(
        max_length=200,
        help_text="Code representing a geography: FIPS code for states and \
        counties, district number for districts, precinct number for \
        precincts, etc.",
    )
    code_components = JSONField(
        blank=True, null=True, help_text="Component parts of code"
    )

    intersecting = models.ManyToManyField(
        "self",
        through="IntersectRelationship",
        symmetrical=False,
        related_name="+",
        help_text="Intersecting divisions intersect this one geographically "
        "but do not necessarily have a parent/child relationship. "
        "The relationship between a congressional district and a "
        "precinct is an example of an intersecting relationship.",
    )

    effective = models.BooleanField(default=True)
    effective_start = models.DateTimeField(null=True, blank=True)
    effective_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        **uid**: :code:`division:{parentuid}_{levelcode}-{code}`
        """
        self.generate_common_identifiers()

        super(Division, self).save(*args, **kwargs)

    def get_uid_suffix(self):
        current_division_slug = "{}={}".format(self.level.slug, self.code)

        if self.parent:
            return "{}&{}".format(
                self.parent.get_uid_suffix(), current_division_slug
            )

        return current_division_slug

    def add_intersecting(self, division, intersection=None, symm=True):
        """
        Adds paired relationships between intersecting divisions.

        Optional intersection represents the portion of the area of the related
        division intersecting this division. You can only specify an
        intersection on one side of the relationship when adding a peer.
        """
        relationship, created = IntersectRelationship.objects.update_or_create(
            from_division=self,
            to_division=division,
            defaults={"intersection": intersection},
        )
        if symm:
            division.add_intersecting(self, None, False)
        return relationship

    def remove_intersecting(self, division, symm=True):
        """Removes paired relationships between intersecting divisions"""
        IntersectRelationship.objects.filter(
            from_division=self, to_division=division
        ).delete()
        if symm:
            division.remove_intersecting(self, False)

    def set_intersection(self, division, intersection):
        """Set intersection percentage of intersecting divisions."""
        IntersectRelationship.objects.filter(
            from_division=self, to_division=division
        ).update(intersection=intersection)

    def get_intersection(self, division):
        """Get intersection percentage of intersecting divisions."""
        try:
            return IntersectRelationship.objects.get(
                from_division=self, to_division=division
            ).intersection
        except ObjectDoesNotExist:
            raise Exception("No intersecting relationship with that division.")

    def has_elections(self, date):
        if len(self.elections.filter(election_day__date=date)) > 0:
            return True

        for child in self.children.all():
            if len(child.elections.filter(election_day__date=date)) > 0:
                return True

        return False
