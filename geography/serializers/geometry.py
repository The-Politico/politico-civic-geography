# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from geography.
from geography.models import Geometry


class GeometrySerializer(NaturalKeySerializerMixin, CommandLineListSerializer):
    class Meta(CommandLineListSerializer.Meta):
        model = Geometry
        fields = "__all__"
