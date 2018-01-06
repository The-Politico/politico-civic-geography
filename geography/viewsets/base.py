from geography.conf import settings
from geography.utils.importers import import_class
from rest_framework import viewsets

authentication = import_class(settings.API_AUTHENTICATION_CLASS)
permission = import_class(settings.API_PERMISSION_CLASS)
pagination = import_class(settings.API_PAGINATION_CLASS)


class BaseViewSet(viewsets.ModelViewSet):
    authentication_classes = (authentication,)
    permission_classes = (permission,)
    pagination_class = pagination
