from django.db import models
from django.core.exceptions import ValidationError


class ItemManager(models.Manager):
    """Manager personalizado para Item con métodos de utilidad."""

    def get_queryset(self):
        return super().get_queryset()

    def by_category(self, category):
        """Retorna los items de una categoría específica."""
        return self.filter(category=category)

    def in_stock(self):
        """Retorna los items con stock disponible."""
        return self.filter(total_stock__gt=0)

    def low_stock(self):
        """Retorna los items con stock bajo (menos del 20%)."""
        return self.filter(
            models.Q(total_stock__gt=0) &
            models.Q(total_stock__lt=models.F('total_stock') * 0.2)
        )


class Item(models.Model):

    class Category(models.TextChoices):
        MOBILIARIO = 'Mobiliario', 'Mobiliario'
        TECH = 'Tecnología e Informática', 'Tecnología e Informática'
        CATERING = 'Catering', 'Catering'
        LOGISTICA = 'Logística', 'Logística'
        AUDIOVISUAL = 'Audiovisual (AV)', 'Audiovisual (AV)'
        SEÑALÉTICA = 'Señalética y Decoración', 'Señalética y Decoración'
        MATERIALES = 'Material de Acreditación', 'Material de Acreditación'
        HERRAMIENTAS = 'Logística y Herramientas', 'Logística y Herramientas'
        SEGURIDAD = 'Seguridad y Salud', 'Seguridad y Salud'
        SUMINISTROS = 'Catering y Suministros', 'Catering y Suministros'

    class Status(models.TextChoices):
        EN_STOCK = 'En Stock', 'En Stock'
        STOCK_BAJO = 'Stock Bajo', 'Stock Bajo'
        SIN_STOCK = 'Sin Stock', 'Sin Stock'

    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Recurso'
    )
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        verbose_name='Categoría'
    )
    total_stock = models.PositiveIntegerField(
        verbose_name='Stock Total'
    )
    image = models.ImageField(
        upload_to='inventory/items/',
        null=True,
        blank=True,
        verbose_name='Imagen'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )

    objects = ItemManager()

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category', 'name']),
        ]

    def __str__(self):
        return self.name

    @property
    def used_stock(self):
        """Calcula dinámicamente el stock usado en asignaciones."""
        return self.assignments.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def available_stock(self):
        """Calcula dinámicamente el stock disponible."""
        return self.total_stock - self.used_stock

    @property
    def status(self):
        """Calcula dinámicamente el estado del stock."""
        available = self.available_stock
        total = self.total_stock
        
        if total == 0:
            return self.Status.SIN_STOCK
        
        if available == 0:
            return self.Status.SIN_STOCK
        
        ratio = available / total if total > 0 else 0
        
        # Stock Bajo si disponibilidad <= 30% del total o <= 1 unidad
        if ratio <= 0.30 or available <= 1:
            return self.Status.STOCK_BAJO
        else:
            return self.Status.EN_STOCK

    def clean(self):
        """Validaciones a nivel de modelo."""
        if self.total_stock is not None and self.total_stock < 0:
            raise ValidationError({'total_stock': 'El stock total no puede ser negativo.'})


class StandAssignment(models.Model):
    
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Recurso'
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad Asignada'
    )
    required_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad Requerida'
    )
    
    # Relación externa hacia la aplicación 'pe_stand'
    stand = models.ForeignKey(
        'pe_stand.Stand',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='item_assignments',
        verbose_name='Stand'
    )
    details = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Detalles'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )

    class Meta:
        verbose_name = 'Asignación a Stand'
        verbose_name_plural = 'Asignaciones a Stands'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item.name} x{self.quantity}"

    def clean(self):
        """Valida que la cantidad no exceda el stock disponible."""
        if self.item_id and self.quantity:
            available = self.item.available_stock
            # Para asignaciones nuevas, no contar la asignación actual
            if self.pk:
                current_assignment = StandAssignment.objects.get(pk=self.pk)
                available += current_assignment.quantity
            
            if self.quantity > available:
                raise ValidationError({
                    'quantity': f'No hay suficiente stock disponible. '
                                f'Stock disponible: {available}. '
                                f'Cantidad solicitada: {self.quantity}.'
                })