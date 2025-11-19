from agendamento.models import Appointment
from .slots import slots_for_day

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