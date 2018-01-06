from geography.models import DivisionLevel
from geography.serializers import DivisionLevelSerializer

from .base import BaseViewSet


class DivisionLevelViewSet(BaseViewSet):
    queryset = DivisionLevel.objects.all()
    serializer_class = DivisionLevelSerializer
