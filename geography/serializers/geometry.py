from geography.models import Geometry
from rest_framework import serializers


class GeometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geometry
        fields = '__all__'
