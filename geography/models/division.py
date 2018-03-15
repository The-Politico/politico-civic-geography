import uuid

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from uuslug import uuslug

from .division_level import DivisionLevel
from .intersect_relationship import IntersectRelationship


class Division(models.Model):
    """
    A political or administrative geography.

    For example, a particular state, county, district, precinct or
    municipality.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uid = models.CharField(
        max_length=500,
        editable=False,
        blank=True
    )

    slug = models.SlugField(
        blank=True, max_length=255,
        unique=True, editable=False)

    name = models.CharField(max_length=255)

    label = models.CharField(max_length=255, blank=True)
    short_label = models.CharField(max_length=50, null=True, blank=True)

    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children')

    level = models.ForeignKey(
        DivisionLevel,
        on_delete=models.PROTECT,
        related_name='divisions')

    code = models.CharField(
        max_length=200,
        help_text="Code representing a geography: FIPS code for states and \
        counties, district number for districts, precinct number for \
        precincts, etc."
    )
    code_components = JSONField(
        blank=True,
        null=True,
        help_text="Component parts of code"
    )

    intersecting = models.ManyToManyField(
        'self',
        through='IntersectRelationship',
        symmetrical=False,
        related_name='+',
        help_text="Intersecting divisions intersect this one geographically "
                  "but do not necessarily have a parent/child relationship. "
                  "The relationship between a congressional district and a "
                  "precinct is an example of an intersecting relationship."
    )

    effective = models.BooleanField(default=True)
    effective_start = models.DateTimeField(null=True, blank=True)
    effective_end = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        **uid**: :code:`division:{parentuid}_{levelcode}-{code}`
        """
        slug = '{}:{}'.format(self.level.uid, self.code)
        if self.parent:
            self.uid = '{}_{}'.format(self.parent.uid, slug)
        else:
            self.uid = slug
        self.slug = uuslug(
            self.name,
            instance=self,
            max_length=100,
            separator='-',
            start_no=2
        )
        super(Division, self).save(*args, **kwargs)

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
            defaults={'intersection': intersection}
        )
        if symm:
            division.add_intersecting(self, None, False)
        return relationship

    def remove_intersecting(self, division, symm=True):
        """Removes paired relationships between intersecting divisions"""
        IntersectRelationship.objects.filter(
            from_division=self,
            to_division=division
        ).delete()
        if symm:
            division.remove_intersecting(self, False)

    def set_intersection(self, division, intersection):
        """Set intersection percentage of intersecting divisions."""
        IntersectRelationship.objects.filter(
            from_division=self,
            to_division=division
        ).update(intersection=intersection)

    def get_intersection(self, division):
        """Get intersection percentage of intersecting divisions."""
        try:
            return IntersectRelationship.objects.get(
                from_division=self,
                to_division=division
            ).intersection
        except ObjectDoesNotExist:
            raise Exception('No intersecting relationship with that division.')

    def __str__(self):
        return self.code
