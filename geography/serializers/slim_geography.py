from geography.models import Geography
from rest_framework import serializers


class SlimGeographySerializer(serializers.ModelSerializer):
    subdivision_level = serializers.SerializerMethodField()
    division = serializers.StringRelatedField()

    def get_subdivision_level(self, obj):
        return obj.subdivision_level.slug

    class Meta:
        model = Geography
        fields = (
            'id',
            'division',
            'subdivision_level',
        )
