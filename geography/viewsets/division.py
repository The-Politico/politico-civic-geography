# Imports from geography.
from geography.models import Division
from geography.serializers import DivisionSerializer
from geography.viewsets.base import BaseViewSet


class DivisionViewSet(BaseViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
