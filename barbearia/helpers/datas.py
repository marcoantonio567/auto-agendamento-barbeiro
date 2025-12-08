from datetime import date as ddate, datetime, timedelta
from django.http import HttpResponseBadRequest, JsonResponse

def get_future_days():
    """Retorna uma lista com os próximos 8 dias a partir de hoje."""
    return [(ddate.today() + timedelta(days=i)) for i in range(0, 8)]

def convert_str_to_date(date_str):
    """Converte string no formato YYYY-MM-DD para date."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def json_empty_hours():
    """Retorna um JSON com uma lista vazia de horas."""
    return JsonResponse({'hours': []})

def convert_str_to_time(hour_str):
    """Converte string no formato HH:MM para time."""
    return datetime.strptime(hour_str, '%H:%M').time()

def convert_str_to_day_and_hour(date_str, hour_str):
    """Converte strings de data e hora e retorna (day, hr) ou 400 se inválido."""
    try:
        day = convert_str_to_date(date_str)
        hr = convert_str_to_time(hour_str)
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
