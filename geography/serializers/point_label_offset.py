from geography.models import PointLabelOffset
from rest_framework import serializers


class PointLabelOffsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointLabelOffset
        fields = '__all__'
