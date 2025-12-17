from core.helpers.validacao import get_hours_delta_from_direction
from core.helpers.datas import shift_hour_by_delta
from core.helpers.slots import is_valid_slot_for_day
from core.helpers.disponibilidade import horario_ja_ocupado


def compute_new_hour(appointment, direction):
    """Calcula e valida a nova hora após mover 1h para trás/à frente.
    
    - direction: 'prev' ou 'next'
    - retorna (new_hour, error_code) onde error_code pode ser:
      'invalid_direction', 'invalid_slot', 'occupied' ou None quando ok
    """
    # Obtém delta a partir da direção; None quando inválida
    hours_delta = get_hours_delta_from_direction(direction)
    if hours_delta is None:
        return None, 'invalid_direction'
    # Aplica delta na hora atual do agendamento
    new_hour = shift_hour_by_delta(appointment.date, appointment.hour, hours_delta)
    # Valida slot do dia
    if not is_valid_slot_for_day(appointment.date, new_hour):
        return None, 'invalid_slot'
    # Valida conflito com outro agendamento do barbeiro
    if horario_ja_ocupado(appointment.barber, appointment.date, new_hour):
        return None, 'occupied'
    return new_hour, None


def apply_hour_shift(appointment, new_hour):
    """Atualiza o agendamento com a nova hora e marca como 'rescheduled'."""
    appointment.hour = new_hour
    appointment.rescheduled = True
    appointment.save(update_fields=['hour', 'rescheduled'])
    return appointment

