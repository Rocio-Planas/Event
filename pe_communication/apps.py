from django.apps import AppConfig


class PeCommunicationConfig(AppConfig):
    name = 'pe_communication'

    def ready(self):
        import pe_communication.signals  # noqa
