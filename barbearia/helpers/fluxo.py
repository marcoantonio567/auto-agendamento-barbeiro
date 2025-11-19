from django.shortcuts import redirect
from django.http import Http404
from django.core.signing import Signer, BadSignature
from agendamento.models import Appointment
from django.shortcuts import get_object_or_404
from barbearia.helpers.datas import converter_str_para_date, converter_str_para_time

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

def get_appointment_by_sid_or_404(sid):
    """
    Obtém um agendamento pelo sid ou retorna 404 se não encontrado.
    """
    try:
        ap_id = Signer().unsign(sid)
    except BadSignature:
        raise Http404
    return get_object_or_404(Appointment, pk=ap_id)

def listar_agendamentos_filtrados(barber, day_str, hour_str):
    qs = Appointment.objects.all().order_by('date', 'hour', 'barber')
    if barber:
        qs = qs.filter(barber=barber)
    if day_str:
        day = converter_str_para_date(day_str)
        if day:
            qs = qs.filter(date=day)
    if hour_str:
        try:
            hr = converter_str_para_time(hour_str)
            qs = qs.filter(hour=hr)
        except ValueError:
            pass
    return qs