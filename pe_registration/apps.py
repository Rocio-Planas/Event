from django.apps import AppConfig


class PeRegistrationConfig(AppConfig):
    name = 'pe_registration'

    def ready(self):
        import pe_registration.signals  # noqa: F401
