from geography.models import DivisionLevel
from geography.serializers import (DivisionLevelSerializer,
                                   SlimDivisionLevelSerializer)
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAdminUser


class DivisionLevelViewSet(viewsets.ModelViewSet):
    queryset = DivisionLevel.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    serializer_class = DivisionLevelSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return SlimDivisionLevelSerializer
        else:
            return DivisionLevelSerializer
