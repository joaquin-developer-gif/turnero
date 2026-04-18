from django.db import models
import datetime
import uuid

class StoreConfig(models.Model):
    open_time = models.TimeField('Horario de apertura', default=datetime.time(8, 0))
    close_time = models.TimeField('Horario de cierre', default=datetime.time(21, 0))
    interval_minutes = models.IntegerField('Intervalo (min)', default=30)
    cancellation_limit_hours = models.IntegerField('Límite de Cancelación (horas)', default=24)
    
    class Meta:
        verbose_name = 'Configuración de Turnos'
        verbose_name_plural = 'Configuraciones de Turnos'

    def __str__(self):
        return "Configuración General"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
        ('completed', 'Completado'),
        ('absent', 'Ausente'),
    ]

    client_name = models.CharField('Nombre', max_length=100)
    client_last_name = models.CharField('Apellido', max_length=100)
    phone = models.CharField('Teléfono', max_length=20)
    
    date = models.DateField('Fecha')
    time = models.TimeField('Hora')
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='pending')
    token = models.UUIDField('Token único', default=uuid.uuid4, editable=False, unique=True)
    
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    
    class Meta:
        unique_together = ('date', 'time')
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.date} {self.time} - {self.client_name} {self.client_last_name}"
