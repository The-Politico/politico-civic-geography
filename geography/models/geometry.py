import json
import uuid

from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.safestring import mark_safe

from .division import Division
from .division_level import DivisionLevel


class Geometry(models.Model):
    """
    The spatial representation (in topoJSON) of a Division.
    """
    D3 = '''
        <div id="map{0}"></div>
        <script>
        var data{0} = {1};
        var feature{0} = topojson.feature(
            data{0}, data{0}.objects['-']);
        var svg{0} = d3.select("#map{0}").append("svg")
            .attr("width", {2})
            .attr("height", {2});
        svg{0}.append("path").datum(feature{0})
            .attr("d", d3.geoPath().projection(
                d3.geoAlbersUsa().scale(1)
                .fitSize([{2}, {2}], feature{0})
            ));
        </script>
    '''

    def small_preview(self):
        return mark_safe(
            self.D3.format(self.pk.hex.replace('-', ''), self.topojson, '60')
        )

    def large_preview(self):
        return mark_safe(
            self.D3.format(self.pk.hex.replace('-', ''), self.topojson, '400')
        )

    def file_size(self):
        return '~{} kB'.format(
            round(len(json.dumps(self.topojson)) / 1000)
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="geometries"
    )
    subdivision_level = models.ForeignKey(
        DivisionLevel,
        on_delete=models.PROTECT,
        related_name="+"
    )
    simplification = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        help_text="Minimum quantile of planar \
        triangle areas for simplfying topojson."
    )
    topojson = JSONField()

    source = models.URLField(
        blank=True, null=True,
        help_text="Link to the source of this geography data.")

    series = models.CharField(
        blank=True, null=True, max_length=4,
        help_text="Year of boundary series, e.g., 2016 TIGER/Line files."
    )

    effective = models.BooleanField(default=True)
    effective_start = models.DateField(null=True, blank=True)
    effective_end = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Geometries"

    def __str__(self):
        return '{} - {} map, {}'.format(
            self.division.label,
            self.division.level.name,
            self.simplification
        )
