# Imports from Django.
from django.contrib.postgres.fields import JSONField
from django.db import models


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UniqueIdentifierMixin


class Point(UniqueIdentifierMixin, CivicBaseModel):
    """A point is a city."""

    natural_key_fields = ["geometry", "label", "lat", "lon"]
    uid_prefix = "point"

    geometry = models.ForeignKey(
        "Geometry", on_delete=models.CASCADE, related_name="points"
    )

    lat = models.FloatField(
        help_text="Latitude coordinate in decimal degrees."
    )
    lon = models.FloatField(
        help_text="Longitude coordinate in decimal degrees."
    )

    attributes = JSONField(
        blank=True,
        null=True,
        help_text="Miscellaneous attributes on the point.",
    )

    threshold = models.PositiveSmallIntegerField(
        default=0,
        help_text="A threshold in pixels above which to display this point.",
    )

    label = models.CharField(max_length=250)

    class Meta:
        unique_together = ("geometry", "label", "lat", "lon")

    def __str__(self):
        return "{}, {}".format(self.label, self.geometry.division.name)

    def get_uid_suffix(self):
        return (
            f"geometry={self.geometry.uid}"
            f"&label={self.label}"
            f"&coords={self.lat},{self.lon}"
        )

    def to_topojson(self):
        offsets = (
            [offset.to_object() for offset in self.offsets.all()]
            if len(self.offsets.all()) > 0
            else None
        )
        return {
            "type": "Point",
            "coordinates": [self.lon, self.lat],
            "properties": {
                "label": self.label,
                "threshold": self.threshold,
                "attributes": self.attributes,
                "offsets": offsets,
            },
        }


class PointLabelOffset(UniqueIdentifierMixin, CivicBaseModel):
    """Offsets used to display a Point's label."""

    natural_key_fields = ["point", "threshold"]
    uid_prefix = "pointlabel"

    point = models.ForeignKey(
        Point, on_delete=models.CASCADE, related_name="offsets"
    )
    x = models.SmallIntegerField(
        default=0, help_text="Lateral offset in pixels."
    )
    y = models.SmallIntegerField(
        default=0, help_text="Vertical offset in pixels."
    )
    threshold = models.PositiveSmallIntegerField(
        default=0,
        help_text="A threshold in pixels above which to apply this offset.",
    )

    def __str__(self):
        return "{} @ {}".format(self.threshold, self.point)

    def get_uid_suffix(self):
        return f"point={self.point.uid}&threshold={self.threshold}"

    def to_object(self):
        return {"threshold": self.threshold, "x": self.x, "y": self.y}
