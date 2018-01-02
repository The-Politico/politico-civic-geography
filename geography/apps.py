from django.apps import AppConfig


class GeographyConfig(AppConfig):
    name = 'geography'

    def ready(self):
        from geography import signals  # noqa
