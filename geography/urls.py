from django.urls import include, path
from rest_framework import routers

from .viewsets import DivisionViewSet, GeographyViewSet

router = routers.DefaultRouter()

router.register(r'divisions', DivisionViewSet)
router.register(r'geographies', GeographyViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
