# Imports from python.
import json
import uuid


# Imports from Django.
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.safestring import mark_safe


# Imports from other dependencies.
from civic_utils.models import CivicBaseModel
from civic_utils.models import UniqueIdentifierMixin
from civic_utils.models import UUIDMixin


# Imports from geography.
from geography.models.division import Division
from geography.models.division_level import DivisionLevel


class Geometry(UniqueIdentifierMixin, UUIDMixin, CivicBaseModel):
    """The spatial representation (in TopoJSON) of a Division."""

    D3 = """
        <div id="map{0}"></div>
        <script>
        var data{0} = {1};
        var feature{0} = topojson.feature(
            data{0}, data{0}.objects.divisions);
        var projection{0} = d3.geoMercator().scale(1)
            .fitSize([{2}, {2}], feature{0});
        var points{0} = data{0}.objects.points ? topojson.feature(
            data{0}, data{0}.objects.points).features : [];
        var svg{0} = d3.select("#map{0}").append("svg")
            .attr("width", {2})
            .attr("height", {2});
        svg{0}.append("path").datum(feature{0})
            .attr("d", d3.geoPath().projection(
                projection{0}
            ));
        svg{0}.selectAll('circle.c{0}')
            .data(points{0})
          .enter().append('circle')
            .attr('class', 'c{0}')
            .attr('cx', function(d) {{
                return projection{0}(d.geometry.coordinates)[0];
            }})
            .attr('cy', function(d) {{
                return projection{0}(d.geometry.coordinates)[1];
            }})
            .attr('r', {2} < 100 ? 2 : 4)
            .attr('fill', 'transparent')
            .attr('stroke-width', {2} < 100 ? 1 : 2)
            .attr('stroke', 'black');
        svg{0}.selectAll('text.t{0}')
            .data(points{0})
        .enter().append('text')
            .text(function(d) {{
                return d.properties.label
            }})
            .attr('x', function(d) {{
                var offset = -10;
                if (d.properties.attributes) {{
                    offset = d.properties.attributes['0'][0];
                }}

                return projection{0}(d.geometry.coordinates)[0] + offset;
            }})
            .attr('y', function(d) {{
                var offset = 4;
                if (d.properties.attributes) {{
                    offset = d.properties.attributes['0'][1];
                }}

                return projection{0}(d.geometry.coordinates)[1] + offset;
            }})
            .attr('fill', 'black')
            .attr('text-anchor', 'end');
        </script>
    """
    natural_key_fields = ["division", "subdivision_level", "data_summary"]
    uid_prefix = "geometry"
    # default_serializer = ""

    division = models.ForeignKey(
        Division, on_delete=models.CASCADE, related_name="geometries"
    )

    subdivision_level = models.ForeignKey(
        DivisionLevel, on_delete=models.PROTECT, related_name="+"
    )

    data_summary = models.SlugField(
        blank=True,
        max_length=255,
        unique=True,
        editable=False,
        help_text=(
            "A brief description (written as a slug) of what makes this data "
            "unique from other Geometry instances with the same 'division' "
            "and 'subdivision_level' values."
        ),
    )

    simplification = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=(
            "Minimum quantile of planar triangle areas for "
            "simplfying topojson."
        ),
    )

    topojson = JSONField()

    source = models.URLField(
        blank=True,
        null=True,
        help_text="Link to the source of this geography data.",
    )

    series = models.CharField(
        blank=True,
        null=True,
        max_length=4,
        help_text="Year of boundary series, e.g., 2016 TIGER/Line files.",
    )

    effective = models.BooleanField(default=True)

    effective_start = models.DateField(null=True, blank=True)

    effective_end = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("division", "subdivision_level", "data_summary")
        verbose_name_plural = "Geometries"

    def __str__(self):
        return "{} - {} map, {}".format(
            self.division.label,
            self.subdivision_level.name,
            self.simplification,
        )

    def save(self, *args, **kwargs):
        self.generate_unique_identifier()

        super(Geometry, self).save(*args, **kwargs)

    def get_uid_suffix(self):
        return (
            f"division={self.division.uid}"
            f"&subdivision_level={self.subdivision_level.uid}"
            f"&data_summary={self.data_summary}"
        )

    def small_preview(self):
        return mark_safe(
            self.D3.format(
                self.pk.hex.replace("-", ""), self.to_topojson(), "60"
            )
        )

    def large_preview(self):
        return mark_safe(
            self.D3.format(
                self.pk.hex.replace("-", ""), self.to_topojson(), "400"
            )
        )

    def file_size(self):
        return "~{} kB".format(round(len(self.to_topojson()) / 1000))

    def to_topojson(self):
        """Adds points and converts to topojson string."""
        topojson = self.topojson
        topojson["objects"]["points"] = {
            "type": "GeometryCollection",
            "geometries": [point.to_topojson() for point in self.points.all()],
        }
        return json.dumps(topojson)
