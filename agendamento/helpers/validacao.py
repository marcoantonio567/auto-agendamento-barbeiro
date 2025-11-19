from datetime import date as ddate, timedelta
from .slots import slots_for_day

def dia_e_hora_validos(day, hr):
    """Confere se o dia está dentro dos próximos 7 dias e se a hora é válida."""
    today = ddate.today()
    if day < today or day > today + timedelta(days=7):
        return False
    return hr in slots_for_day(day)