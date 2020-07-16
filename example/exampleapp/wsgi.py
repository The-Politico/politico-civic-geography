# Imports from python.
import os


# Imports from Django.
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exampleapp.settings")

application = get_wsgi_application()
