from django.test import TestCase
from django.urls import reverse
from datetime import date, time, timedelta, datetime
from scheduling.models import Appointment
from core.helpers.disponibilidade import taken_hours, horario_ja_ocupado, available_hours_for_day
from core.helpers.validacao import dia_e_hora_validos
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


class HorariosHojeTests(TestCase):
    def test_available_hours_excludes_past_and_keeps_future_today(self):
        today = date.today()
        now = datetime.now()
        if now.hour <= 7 or now.hour >= 19:
            self.skipTest('Sem slots anteriores ou futuros dentro do intervalo de 07:00–19:00.')
        past_slot = time(now.hour - 1, 0)
        future_slot = time(now.hour + 1, 0)
        hours = available_hours_for_day('Japa', today)
        past_str = past_slot.strftime('%H:%M')
        future_str = future_slot.strftime('%H:%M')
        self.assertNotIn(past_str, hours)
        self.assertIn(future_str, hours)

    def test_dia_e_hora_validos_hoje(self):
        today = date.today()
        now = datetime.now()
        if now.hour <= 7 or now.hour >= 19:
            self.skipTest('Sem slots anteriores ou futuros dentro do intervalo de 07:00–19:00.')
        past_slot = time(now.hour - 1, 0)
        future_slot = time(now.hour + 1, 0)
        self.assertFalse(dia_e_hora_validos(today, past_slot))
        self.assertTrue(dia_e_hora_validos(today, future_slot))

    def test_api_sincroniza_com_helper(self):
        today = date.today()
        hours_helper = available_hours_for_day('Japa', today)
        url = reverse('horarios_api')
        resp = self.client.get(url, {'barber': 'Japa', 'date': today.strftime('%Y-%m-%d')})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('hours'), hours_helper)

    def test_step_client_mensagem_erro_para_horario_passado(self):
        today = date.today()
        now = datetime.now()
        if now.hour <= 7:
            self.skipTest('Sem slot passado dentro do intervalo de 07:00–19:00.')
        past_slot = time(now.hour - 1, 0)
        session = self.client.session
        session['service'] = 'cabelo'
        session['barber'] = 'Japa'
        session['date'] = today.strftime('%Y-%m-%d')
        session['hour'] = past_slot.strftime('%H:%M')
        session.save()
        url = reverse('step_client')
        resp = self.client.post(url, {'client_name': 'Teste', 'client_phone': '(11) 9 9999-9999'})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Horário já passou', resp.content.decode('utf-8'))
