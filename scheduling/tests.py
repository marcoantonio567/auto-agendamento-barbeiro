from django.test import TestCase
from datetime import date, time, timedelta
from scheduling.models import Appointment
from core.helpers.disponibilidade import taken_hours, horario_ja_ocupado
from core.helpers.fluxo import list_filtered_appointments


class CancelamentoDisponibilidadeTests(TestCase):
    def setUp(self):
        self.day = date.today() + timedelta(days=1)
        self.hour = time(10, 0)
        self.ap = Appointment.objects.create(
            client_name='Cliente Teste',
            client_phone='1199999999',
            service='cabelo',
            barber='Japa',
            date=self.day,
            hour=self.hour,
            status='ativo',
        )

    def test_taken_hours_considera_ativo(self):
        horas_tomadas = taken_hours('Japa', self.day)
        self.assertIn(self.hour, horas_tomadas)
        self.assertTrue(horario_ja_ocupado('Japa', self.day, self.hour))

    def test_disponibilidade_libera_apos_cancelar(self):
        self.ap.status = 'cancelado'
        self.ap.save(update_fields=['status'])
        horas_tomadas = taken_hours('Japa', self.day)
        self.assertNotIn(self.hour, horas_tomadas)
        self.assertFalse(horario_ja_ocupado('Japa', self.day, self.hour))

    def test_list_filtered_exclui_cancelados(self):
        qs = list_filtered_appointments('Japa', self.day.strftime('%Y-%m-%d'), None)
        self.assertIn(self.ap, qs)
        # cancelar e verificar exclusão
        self.ap.status = 'cancelado'
        self.ap.save(update_fields=['status'])
        qs2 = list_filtered_appointments(None, None, None)
        self.assertNotIn(self.ap, qs2)
