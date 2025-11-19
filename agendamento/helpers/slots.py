from datetime import time

def slots_for_day(dt):
    """Gera horários padrão (07:00–18:00, de hora em hora) para um dia."""
    slots = []
    for h in range(7, 19):
        slots.append(time(hour=h, minute=0))
    return slots