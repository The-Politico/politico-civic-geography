from geography.models import Geography
from geography.serializers import GeographySerializer, SlimGeographySerializer
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser


class ResultsPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


class GeographyViewSet(viewsets.ModelViewSet):
    queryset = Geography.objects.all()
    pagination_class = ResultsPagination
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == 'list':
            return SlimGeographySerializer
        else:
            return GeographySerializer
