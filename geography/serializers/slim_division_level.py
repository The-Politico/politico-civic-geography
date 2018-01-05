from geography.models import DivisionLevel
from rest_framework import serializers


class SlimDivisionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivisionLevel
        fields = (
            'id',
            'slug',
        )
