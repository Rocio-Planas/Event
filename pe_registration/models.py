from in_person_events.models import Event
from django.db import models
from django.conf import settings

class TicketType(models.Model):
    """
    Tabla para definir los tipos de entrada disponibles en la creación.
    """
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='ticket_types'
    )
    name = models.CharField(max_length=100, verbose_name='Nombre del Ticket')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')

    def __str__(self):
        return f"{self.name} - {self.event.title}"