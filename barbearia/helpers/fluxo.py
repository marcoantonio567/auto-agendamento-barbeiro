from django.shortcuts import redirect
from django.http import Http404
from django.core.signing import Signer, BadSignature
from agendamento.models import Appointment
from django.shortcuts import get_object_or_404
from barbearia.helpers.datas import convert_str_to_date, convert_str_to_time
from datetime import time, date, datetime
from django.db.models import Q

def criar_agendamento_e_redirecionar(request, client_name, client_phone, service, barber, day, hr):
    ap = Appointment.objects.create(
        client_name=client_name,
        client_phone=client_phone,
        service=service,
        barber=barber,
        date=day,
        hour=hr,
    )
    request.session.flush()
    sid = Signer().sign(ap.id)
    return redirect('pagamento', sid=sid)

def get_datas_step_client(request):
    client_name = request.POST.get('client_name')
    client_phone = request.POST.get('client_phone')
    service = request.session.get('service')
    barber = request.session.get('barber')
    date_str = request.session.get('date')
    hour_str = request.session.get('hour')
    if not all([client_name, client_phone, service, barber, date_str, hour_str]):
        return None
    return client_name, client_phone, service, barber, date_str, hour_str

def get_appointment_by_sid_or_404(sid):
    """
    Obtém um agendamento pelo sid ou retorna 404 se não encontrado.
    """
    try:
        ap_id = Signer().unsign(sid)
    except BadSignature:
        raise Http404
    return get_object_or_404(Appointment, pk=ap_id)

def list_filtered_appointments(barber, day_str, hour_str):
    """
    Retorna os agendamentos futuros ou do dia/hora atual em diante,
    podendo filtrar por barbeiro, dia e/ou hora.
    """
    qs = Appointment.objects.all().order_by('date', 'hour', 'barber')
    today = date.today()
    now_time = datetime.now().time()
    # Apenas agendamentos a partir de agora
    qs = qs.filter(Q(date__gt=today) | Q(date=today, hour__gte=now_time))
    if barber:
        qs = qs.filter(barber=barber)
    if day_str:
        day = convert_str_to_date(day_str)
        if day:
            qs = qs.filter(date=day)
    if hour_str:
        try:
            if ':' in hour_str:
                hr = convert_str_to_time(hour_str)
                qs = qs.filter(hour=hr)
            else:
                h = int(hour_str)
                start = time(h, 0)
                end = time(h + 1, 0) if h < 23 else None
                if end:
                    qs = qs.filter(hour__gte=start, hour__lt=end)
                else:
                    qs = qs.filter(hour__gte=start)
        except Exception:
            pass
    return qs

def get_hours_opts(qs):
    """
    Retorna as opções de horas únicas a partir de um QuerySet de agendamentos.
    """
    return sorted({h.hour for h in qs.values_list('hour', flat=True)})

def get_dates_opts(qs):
    """
    Retorna as opções de datas únicas a partir de um QuerySet de agendamentos.
    """
    return list(qs.order_by('date').values_list('date', flat=True).distinct())
