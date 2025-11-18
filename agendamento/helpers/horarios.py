from datetime import date as ddate, datetime, time, timedelta
from agendamento.models import Appointment

def slots_for_day(dt):
    """Gera os horários padrão de atendimento para um dia
    (de 07:00 até 18:00, de hora em hora)."""
    slots = []
    for h in range(7, 19):
        slots.append(time(hour=h, minute=0))
    return slots

def sete_dias_futuros():
    """Retorna uma lista com os próximos sete dias a partir de hoje."""
    return [(ddate.today() + timedelta(days=i)) for i in range(0, 8)]

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()

def taken_hours(barber, day):
    return set(Appointment.objects.filter(barber=barber, date=day).values_list('hour', flat=True))

def available_hours_for_day(barber, day):
    taken = taken_hours(barber, day)
    hours = []
    for hr in slots_for_day(day):
        if hr not in taken:
            hours.append(hr.strftime('%H:%M'))
    return hours