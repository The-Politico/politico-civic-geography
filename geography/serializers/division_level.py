from geography.models import DivisionLevel
from rest_framework import serializers


class DivisionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivisionLevel
        fields = (
            'id',
            'uid',
            'slug',
            'name',
            'parent',
        )
