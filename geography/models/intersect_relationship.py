from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class IntersectRelationship(models.Model):
    """
    Each IntersectRelationship instance represents one side of a paired
    relationship between intersecting divisions.

    The intersection field represents the decimal proportion of the
    to_division that intersects with the from_division. It's useful for
    apportioning counts between the areas, for example, population statistics
    from census data.
    """
    from_division = models.ForeignKey(
        'Division',
        on_delete=models.CASCADE,
        related_name="+"
    )
    to_division = models.ForeignKey(
        'Division',
        on_delete=models.CASCADE,
        related_name="+"
    )
    intersection = models.DecimalField(
        max_digits=7,
        decimal_places=6,
        null=True, blank=True,
        help_text="The portion of the to_division that intersects this "
                  "division."
    )

    class Meta:
        # Don't allow duplicate relationships between divisions
        unique_together = ('from_division', 'to_division')

    def clean(self):
        if self.intersection < 0.0 or self.intersection > 1.0:
            raise ValidationError(_(
                'Intersection should be a decimal between 0 and 1.'
            ))
