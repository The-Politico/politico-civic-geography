from geography.models import Division
from geography.serializers import DivisionSerializer
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser


class ResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class DivisionViewSet(viewsets.ModelViewSet):
    serializer_class = DivisionSerializer
    queryset = Division.objects.all()
    pagination_class = ResultsPagination
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
