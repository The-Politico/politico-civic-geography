# Imports from geography.
from geography.models import Point
from geography.serializers import PointSerializer
from geography.viewsets.base import BaseViewSet


class PointViewSet(BaseViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
