from geography.models import Geometry
from rest_framework import serializers


class GeometrySerializer(serializers.ModelSerializer):
    subdivision_level = serializers.SerializerMethodField()
    division = serializers.StringRelatedField()

    def get_subdivision_level(self, obj):
        return obj.subdivision_level.slug

    class Meta:
        model = Geometry
        fields = (
            'id',
            'division',
            'subdivision_level',
            'simplification',
            'source',
            'series',
            'effective',
            'effective_start',
            'effective_end',
            'topojson',
        )
