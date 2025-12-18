from scheduling.models import Appointment
from .slots import slots_for_day
from django.http import JsonResponse
from core.helpers.datas import convert_str_to_date, json_empty_hours
from datetime import datetime, date as ddate

def taken_hours(barber, day):
    """Retorna conjunto de horários já agendados para o barbeiro no dia."""
    return set(Appointment.objects.filter(barber=barber, date=day, status='ativo').values_list('hour', flat=True))

def available_hours_for_day(barber, day):
    """Lista horas disponíveis (como 'HH:MM') para o barbeiro no dia."""
    taken = taken_hours(barber, day)
    hours = []
    now_time = datetime.now().time()
    today = ddate.today()
    for hr in slots_for_day(day):
        if day == today and hr < now_time:
            continue
        if hr not in taken:
            hours.append(hr.strftime('%H:%M'))
    return hours

def horario_ja_ocupado(barber, day, hr):
    """Indica se o horário está ocupado para o barbeiro e dia informados."""
    return Appointment.objects.filter(barber=barber, date=day, hour=hr, status='ativo').exists()

def horarios_disponiveis_response(barber, date_str):
    """Retorna `JsonResponse` com horas disponíveis para o barbeiro na data."""
    day = convert_str_to_date(date_str)
    if not barber or not date_str:
        return json_empty_hours()
    if day is None:
        return json_empty_hours()
    hours = available_hours_for_day(barber, day)
    return JsonResponse({'hours': hours})
