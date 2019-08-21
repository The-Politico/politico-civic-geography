# Imports from geography.
from geography.models import Geometry
from geography.serializers import GeometryListSerializer, GeometrySerializer
from geography.viewsets.base import BaseViewSet


class GeometryViewSet(BaseViewSet):
    queryset = Geometry.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return GeometryListSerializer
        else:
            return GeometrySerializer
