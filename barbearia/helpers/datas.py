from datetime import date as ddate, datetime, timedelta
from django.http import HttpResponseBadRequest, JsonResponse

def sete_dias_futuros():
    """Retorna uma lista com os próximos 8 dias a partir de hoje."""
    return [(ddate.today() + timedelta(days=i)) for i in range(0, 8)]

def converter_str_para_date(date_str):
    """Converte string no formato YYYY-MM-DD para date."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def json_horarios_vazio():
    return JsonResponse({'hours': []})

def converter_str_para_time(hour_str):
    """Converte string no formato HH:MM para time."""
    return datetime.strptime(hour_str, '%H:%M').time()

def converter_str_para_day_e_hora(date_str, hour_str):
    """Converte strings de data e hora e retorna (day, hr) ou 400 se inválido."""
    try:
        day = converter_str_para_date(date_str)
        hr = converter_str_para_time(hour_str)
        return day, hr
    except ValueError:
        return HttpResponseBadRequest()


def shift_hour_by_delta(day, hour, hours_delta):
    """Calcula a nova hora somando/subtraindo um delta de horas.

    - day: data do agendamento (date)
    - hour: hora atual do agendamento (time)
    - hours_delta: inteiro representando o deslocamento de horas
    """
    base_dt = datetime.combine(day, hour)
    return (base_dt + timedelta(hours=hours_delta)).time()
