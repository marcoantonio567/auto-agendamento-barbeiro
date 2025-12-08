from datetime import time

def slots_for_day(dt):
    slots = []
    for h in range(7, 19):
        slots.append(time(hour=h, minute=0))
    return slots


def is_valid_slot_for_day(day, time_obj):
    return time_obj in set(slots_for_day(day))
