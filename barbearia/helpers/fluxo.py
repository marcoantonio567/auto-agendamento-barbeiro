from django.shortcuts import redirect
from agendamento.models import Appointment

def criar_agendamento_e_redirecionar(request, client_name, service, barber, day, hr):
    """Cria o Appointment, limpa sessão e redireciona para a página de pagamento."""
    ap = Appointment.objects.create(
        client_name=client_name,
        service=service,
        barber=barber,
        date=day,
        hour=hr,
    )
    request.session.flush()
    return redirect('pagamento', appointment_id=ap.id)

def obter_dados_step_client(request):
    """Coleta dados do cliente/sessão e retorna tupla ou None se faltar algo."""
    client_name = request.POST.get('client_name')
    service = request.session.get('service')
    barber = request.session.get('barber')
    date_str = request.session.get('date')
    hour_str = request.session.get('hour')
    if not all([client_name, service, barber, date_str, hour_str]):
        return None
    return client_name, service, barber, date_str, hour_str