from datetime import time

def slots_for_day(dt):
    """Retorna horários cheios entre 07:00 e 19:00 para o dia informado."""
    slots = []
    for h in range(7, 20):
        slots.append(time(hour=h, minute=0))
    return slots


def is_valid_slot_for_day(day, time_obj):
    """Verifica se `time_obj` está entre os slots válidos do dia."""
    return time_obj in set(slots_for_day(day))
