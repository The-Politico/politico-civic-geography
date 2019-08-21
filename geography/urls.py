# Imports from python.


# Imports from Django.
from django.urls import include, path


# Imports from other dependencies.
from rest_framework import routers


# Imports from geography.
from geography.viewsets import DivisionLevelViewSet
from geography.viewsets import DivisionViewSet
from geography.viewsets import GeometryViewSet
from geography.viewsets import PointLabelOffsetViewSet
from geography.viewsets import PointViewSet


router = routers.DefaultRouter()


router.register(r"divisions", DivisionViewSet)
router.register(r"geometries", GeometryViewSet)
router.register(r"division-levels", DivisionLevelViewSet)
router.register(r"point-label-offsets", PointLabelOffsetViewSet)
router.register(r"points", PointViewSet)


urlpatterns = [path("api/", include(router.urls))]
