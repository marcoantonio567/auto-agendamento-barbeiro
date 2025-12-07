from datetime import time

def slots_for_day(dt):
    """Gera horários padrão (07:00–18:00, de hora em hora) para um dia."""
    slots = []
    for h in range(7, 19):
        slots.append(time(hour=h, minute=0))
    return slots


def is_valid_slot_for_day(day, time_obj):
    """Verifica se uma hora pertence aos slots válidos do dia.

    - day: data alvo (date)
    - time_obj: hora alvo (time)
    """
    return time_obj in set(slots_for_day(day))
