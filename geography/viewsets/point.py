from geography.models import Point
from geography.serializers import PointSerializer

from .base import BaseViewSet


class PointViewSet(BaseViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
