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
