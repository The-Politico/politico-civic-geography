from django.urls import include, path
from rest_framework import routers

from .viewsets import (DivisionLevelViewSet, DivisionViewSet, GeometryViewSet,
                       PointLabelOffsetViewSet, PointViewSet)

router = routers.DefaultRouter()

router.register(r'divisions', DivisionViewSet)
router.register(r'geometries', GeometryViewSet)
router.register(r'division-levels', DivisionLevelViewSet)
router.register(r'point-label-offsets', PointLabelOffsetViewSet)
router.register(r'points', PointViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
