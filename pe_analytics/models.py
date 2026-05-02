from django.db import models


class StoredReport(models.Model):
    event_id = models.IntegerField(db_index=True)
    total_attendance = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    age_distribution = models.JSONField(default=dict)
    gender_distribution = models.JSONField(default=dict)
    ticket_distribution = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_report = models.FileField(upload_to='reports/', null=True, blank=True)

    class Meta:
        verbose_name = 'Reporte Analítico'
        verbose_name_plural = 'Reportes Analíticos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Reporte Evento {self.event_id} - {self.created_at.strftime("%Y-%m-%d")}'