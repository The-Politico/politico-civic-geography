# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin
from rest_framework import serializers


# Imports from geography.
from geography.models import Geometry


class GeometryListSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    subdivision_level = serializers.SerializerMethodField()
    division = serializers.StringRelatedField()

    def get_subdivision_level(self, obj):
        return obj.subdivision_level.slug

    class Meta(CommandLineListSerializer.Meta):
        model = Geometry
        fields = ("id", "division", "subdivision_level")
