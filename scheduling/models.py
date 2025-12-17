from django.db import models
from django.db.models import UniqueConstraint, Q


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('cancelado', 'Cancelado'),
    ]
    SERVICE_CHOICES = [
        ('barba', 'Fazer a barba'),
        ('cabelo', 'Cortar o cabelo'),
        ('combo', 'Barba + cabelo'),
    ]
    BARBER_CHOICES = [
        ('Japa', 'Japa'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('pix', 'Pix'),
        ('cash', 'Dinheiro'),
    ]
    PAYMENT_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('falhou', 'Falhou'),
    ]
    CANCELLED_BY_CHOICES = [
        ('barber', 'Barbeiro'),
        ('client', 'Cliente'),
        ('system', 'Sistema'),
    ]
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=16, blank=True, default='')
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    barber = models.CharField(max_length=10, choices=BARBER_CHOICES)
    date = models.DateField()
    hour = models.TimeField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='pendente')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    rescheduled = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')
    cancel_reason = models.CharField(max_length=255, blank=True, default='')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.CharField(max_length=10, choices=CANCELLED_BY_CHOICES, blank=True, default='')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['barber', 'date', 'hour'],
                condition=Q(status='ativo'),
                name='unique_active_appointment'
            )
        ]
        db_table = 'agendamento_appointment'

    def price(self):
        if self.service == 'combo':
            return 100
        return 50

    def service_label(self):
        return dict(self.SERVICE_CHOICES).get(self.service)
