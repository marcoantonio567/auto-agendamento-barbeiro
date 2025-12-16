from django.db import models


class Appointment(models.Model):
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
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=16, blank=True, default='')
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    barber = models.CharField(max_length=10, choices=BARBER_CHOICES)
    date = models.DateField()
    hour = models.TimeField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='pendente')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    rescheduled = models.BooleanField(default=False)

    class Meta:
        unique_together = [('barber', 'date', 'hour')]
        db_table = 'agendamento_appointment'

    def price(self):
        if self.service == 'combo':
            return 100
        return 50

    def service_label(self):
        return dict(self.SERVICE_CHOICES).get(self.service)
