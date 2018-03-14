from geography.models import PointLabelOffset
from geography.serializers import PointLabelOffsetSerializer

from .base import BaseViewSet


class PointLabelOffsetViewSet(BaseViewSet):
    queryset = PointLabelOffset.objects.all()
    serializer_class = PointLabelOffsetSerializer
