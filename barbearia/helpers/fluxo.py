from django.shortcuts import redirect
from django.core.signing import Signer
from agendamento.models import Appointment

def criar_agendamento_e_redirecionar(request, client_name, service, barber, day, hr):
    ap = Appointment.objects.create(
        client_name=client_name,
        service=service,
        barber=barber,
        date=day,
        hour=hr,
    )
    request.session.flush()
    sid = Signer().sign(ap.id)
    return redirect('pagamento', sid=sid)

def obter_dados_step_client(request):
    client_name = request.POST.get('client_name')
    service = request.session.get('service')
    barber = request.session.get('barber')
    date_str = request.session.get('date')
    hour_str = request.session.get('hour')
    if not all([client_name, service, barber, date_str, hour_str]):
        return None
    return client_name, service, barber, date_str, hour_str