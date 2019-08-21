# Imports from other dependencies.
from civic_utils.serializers import CommandLineListSerializer
from civic_utils.serializers import NaturalKeySerializerMixin


# Imports from geography.
from geography.models import PointLabelOffset


class PointLabelOffsetSerializer(
    NaturalKeySerializerMixin, CommandLineListSerializer
):
    class Meta(CommandLineListSerializer.Meta):
        model = PointLabelOffset
        fields = "__all__"
