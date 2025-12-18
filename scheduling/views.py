from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.conf import settings
from core.helpers.self_service_token import validar_token
from core.helpers.infos import SERVICES, BARBERS, obter_barbers, obter_barbers_keys
import random
from core.helpers.datas import get_future_days, convert_str_to_date, convert_str_to_day_and_hour
from datetime import date as ddate, timedelta
from core.helpers.disponibilidade import available_hours_for_day, horario_ja_ocupado, horarios_disponiveis_response
from core.helpers.validacao import dia_e_hora_validos , verificar_step
from core.helpers.phone_validation import PhoneValidator
from core.helpers.fluxo import criar_agendamento_e_redirecionar, get_datas_step_client


@require_http_methods(["GET","POST"])
def step_service(request):
    if getattr(settings, 'REQUIRE_SELF_SERVICE_TOKEN', False) and not request.session.get('self_service_ok'):
        return HttpResponseBadRequest()
    if request.method == 'POST':
        request.session['service'] = request.POST.get('service')
        return redirect('step_barber')
    return render(request, 'scheduling/step_service.html', {'services': SERVICES, 'back_url': None})

def step_barber(request):
    verificar_step(request, 'service')
    if request.method == 'POST':
        choice = request.POST.get('barber')
        if choice == 'ANY':
            choice = random.choice(obter_barbers_keys())
        request.session['barber'] = choice
        return redirect('step_date')
    return render(request, 'scheduling/step_barber.html', {'barbers': obter_barbers(), 'back_url': 'step_service'})

def step_date(request):
    verificar_step(request, 'barber')
    if request.method == 'POST':
        request.session['date'] = request.POST.get('date')
        return redirect('step_hour')
    days = get_future_days()
    return render(request, 'scheduling/step_date.html', {'days': days, 'back_url': 'step_barber', 'today': ddate.today(), 'tomorrow': ddate.today() + timedelta(days=1)})

def step_hour(request):
    verificar_step(request, 'date')
    barber = request.session.get('barber')
    date_str = request.session.get('date')
    day = convert_str_to_date(date_str)
    hours = available_hours_for_day(barber, day)
    if request.method == 'POST':
        request.session['hour'] = request.POST.get('hour')
        return redirect('step_client')
    return render(request, 'scheduling/step_hour.html', {'hours': hours, 'back_url': 'step_date', 'barber': barber, 'date_str': date_str})

def step_client(request):
    verificar_step(request, 'hour')
    if request.method == 'POST':
        data = get_datas_step_client(request)
        if not data:
            return HttpResponseBadRequest('Dados incompletos para o agendamento.')
        client_name, client_phone, service, barber, date_str, hour_str = data
        if not PhoneValidator.is_valid_brazil_number(client_phone):
            return HttpResponseBadRequest('Número de telefone inválido.')
        day, hr = convert_str_to_day_and_hour(date_str, hour_str)
        if not dia_e_hora_validos(day, hr):
            return HttpResponseBadRequest('Horário já passou. Escolha um horário futuro.')
        if horario_ja_ocupado(barber, day, hr):
            return HttpResponseBadRequest('Horário indisponível. Selecione outro horário.')
        return criar_agendamento_e_redirecionar(request, client_name, client_phone, service, barber, day, hr)
    return render(request, 'scheduling/step_client.html', {'back_url': 'step_hour'})


@require_http_methods(["GET"])
def horarios_api(request):
    barber = request.GET.get('barber')
    date_str = request.GET.get('date')
    return horarios_disponiveis_response(barber, date_str)


@require_http_methods(["GET"])
def self_service_entry(request):
    token = request.GET.get('t') or request.GET.get('token')
    if not token:
        return HttpResponseBadRequest()
    data = validar_token(token)
    if not data:
        return HttpResponseBadRequest()
    request.session['self_service_ok'] = True
    service = data.get('service')
    barber = data.get('barber')
    client_phone = data.get('client_phone')
    if service:
        request.session['service'] = service
    if barber:
        request.session['barber'] = barber
    if client_phone:
        request.session['client_phone_prefill'] = client_phone
    if request.session.get('service') and request.session.get('barber'):
        return redirect('step_date')
    if request.session.get('service'):
        return redirect('step_barber')
    return redirect('step_service')
