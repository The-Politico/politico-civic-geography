from django.contrib.postgres.fields import JSONField
from django.db import models


class Point(models.Model):
    """A point is a city."""
    geometry = models.ForeignKey(
        'Geometry',
        on_delete=models.CASCADE,
        related_name="points"
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
        help_text="Miscellaneous attributes on the point."
    )

    threshold = models.PositiveSmallIntegerField(
        default=0,
        help_text="A threshold in pixels above which to display this point."
    )

    label = models.CharField(max_length=250)

    def to_topojson(self):
        offsets = [
            offset.to_object() for offset
            in self.offsets.all()
        ] if len(self.offsets.all()) > 0 else None
        return {
            'type': 'Point',
            'coordinates': [
                self.lon,
                self.lat
            ],
            'properties': {
                'label': self.label,
                'threshold': self.threshold,
                'attributes': self.attributes,
                'offsets': offsets,
            }
        }

    def __str__(self):
        return '{}, {}'.format(
            self.label,
            self.geometry.division.name
        )


class PointLabelOffset(models.Model):
    """Offsets used to display a Point's label."""
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
        related_name="offsets"
    )
    x = models.SmallIntegerField(
        default=0,
        help_text="Lateral offset in pixels.",
    )
    y = models.SmallIntegerField(
        default=0,
        help_text="Vertical offset in pixels.",
    )
    threshold = models.PositiveSmallIntegerField(
        default=0,
        help_text="A threshold in pixels above which to apply this offset."
    )

    def to_object(self):
        return {
            'threshold': self.threshold,
            'x': self.x,
            'y': self.y
        }

    def __str__(self):
        return '{} @ {}'.format(self.threshold, self.point)
