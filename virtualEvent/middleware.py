from django.utils.deprecation import MiddlewareMixin
from .models import EventAnalytics, EventView, VirtualEvent


class VisitTrackingMiddleware(MiddlewareMixin):
    """Registra una visita única (por sesión) al acceder a streaming_room."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Detectamos la vista 'streaming_room' de ve_streaming
        if view_func.__name__ == "streaming_room" and "unique_link" in view_kwargs:
            unique_link = view_kwargs["unique_link"]
            try:
                event = VirtualEvent.objects.get(unique_link=unique_link)
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                ip = request.META.get("REMOTE_ADDR")
                # Registrar vista única si no existe
                EventView.objects.get_or_create(
                    event=event, session_key=session_key, defaults={"ip_address": ip}
                )
                # Actualizar contador de espectadores únicos en analytics
                analytics, _ = EventAnalytics.objects.get_or_create(event=event)
                unique_count = (
                    EventView.objects.filter(event=event)
                    .values("session_key")
                    .distinct()
                    .count()
                )
                if analytics.unique_viewers != unique_count:
                    analytics.unique_viewers = unique_count
                    analytics.save(update_fields=["unique_viewers"])
            except VirtualEvent.DoesNotExist:
                pass
        return None
