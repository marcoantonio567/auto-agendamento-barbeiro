from datetime import date, datetime
from django.db.models import Q
from scheduling.models import Appointment


def get_past_appointments(barber=None, start=None, end=None):
    """Retorna agendamentos já passados, com filtros opcionais.
    
    - barber: filtra pelo barbeiro informado
    - start/end: intervalo de datas (inclusive)
    - ordena por data e hora em ordem decrescente
    """
    # Descobre "hoje" e a hora atual para considerar horários já passados
    today = date.today()
    now_time = datetime.now().time()
    # Monta queryset com agendamentos anteriores a agora
    qs = Appointment.objects.filter(Q(date__lt=today) | Q(date=today, hour__lt=now_time))
    # Aplica filtros opcionais
    if barber:
        qs = qs.filter(barber=barber)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    # Ordena para exibição no histórico
    return qs.order_by('-date', '-hour')

