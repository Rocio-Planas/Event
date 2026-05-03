from django.apps import AppConfig


class AgendaConfig(AppConfig):
    name = 'pe_agenda'

    def ready(self):
        import pe_agenda.signals  # noqa