from agendamento.models import Appointment
from .slots import slots_for_day
from django.http import JsonResponse
from barbearia.helpers.datas import convert_str_to_date, json_empty_hours

def taken_hours(barber, day):
    """Retorna um conjunto de horas já ocupadas para o barbeiro no dia."""
    return set(Appointment.objects.filter(barber=barber, date=day).values_list('hour', flat=True))

def available_hours_for_day(barber, day):
    """Lista horas disponíveis (HH:MM) para o barbeiro no dia informado."""
    taken = taken_hours(barber, day)
    hours = []
    for hr in slots_for_day(day):
        if hr not in taken:
            hours.append(hr.strftime('%H:%M'))
    return hours

def horario_ja_ocupado(barber, day, hr):
    """Verifica se já existe agendamento para barbeiro/dia/hora."""
    return Appointment.objects.filter(barber=barber, date=day, hour=hr).exists()

def horarios_disponiveis_response(barber, date_str):
    """
    Retorna um JsonResponse com a lista de horários disponíveis para o barbeiro no dia informado.
    """
    day = convert_str_to_date(date_str)
    if not barber or not date_str:
        return json_empty_hours()
    if day is None:
        return json_empty_hours()
    hours = available_hours_for_day(barber, day)
    return JsonResponse({'hours': hours})