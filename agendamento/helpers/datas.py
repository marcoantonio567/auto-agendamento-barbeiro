from datetime import date as ddate, datetime, timedelta
from django.http import HttpResponseBadRequest

def sete_dias_futuros():
    """Retorna uma lista com os próximos 8 dias a partir de hoje."""
    return [(ddate.today() + timedelta(days=i)) for i in range(0, 8)]

def converter_str_para_date(date_str):
    """Converte string no formato YYYY-MM-DD para date."""
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def parse_date(date_str):
    """Atalho para converter string YYYY-MM-DD em date."""
    return converter_str_para_date(date_str)

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