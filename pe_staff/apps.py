from django.apps import AppConfig


class PeStaffConfig(AppConfig):
    name = 'pe_staff'

    def ready(self):
        import pe_staff.signals  # noqa: F401
