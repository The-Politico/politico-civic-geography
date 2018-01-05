from geography.models import Division
from rest_framework import serializers

from .related_division import RelatedDivisionSerializer


class SlimDivisionSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    parent = RelatedDivisionSerializer()

    def get_level(self, obj):
        return obj.level.slug

    class Meta:
        model = Division
        fields = (
            'id',
            'level',
            'name',
            'parent',
        )
