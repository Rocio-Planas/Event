from django.apps import AppConfig


class VirtualEventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'virtualEvent'

    def ready(self):
        import virtualEvent.signals  # noqa: F401
