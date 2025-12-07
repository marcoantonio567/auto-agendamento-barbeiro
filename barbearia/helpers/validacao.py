from datetime import date as ddate, timedelta
from .slots import slots_for_day
from django.shortcuts import redirect



def dia_e_hora_validos(day, hr):
    """Confere se o dia está dentro dos próximos 7 dias e se a hora é válida."""
    today = ddate.today()
    if day < today or day > today + timedelta(days=7):
        return False
    return hr in slots_for_day(day)

def verificar_step(request, step):
    """
    Verifica se o usuário passou na etapa do anterior.
    Se não estiver, redireciona para a etapa do anterior.
    """
    if not request.session.get(step):
        return redirect(f'step_{step}')


def get_hours_delta_from_direction(direction):
    """Retorna o delta de horas a partir da direção.

    - direction: 'prev' -> -1 hora, 'next' -> +1 hora
    - retorna None se a direção for inválida
    """
    if direction == 'prev':
        return -1
    if direction == 'next':
        return 1
    return None
