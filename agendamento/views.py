from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from core.helpers.infos import SERVICES, BARBERS
from core.helpers.datas import get_future_days, convert_str_to_date, convert_str_to_day_and_hour
from core.helpers.disponibilidade import available_hours_for_day, horario_ja_ocupado, horarios_disponiveis_response
from core.helpers.validacao import dia_e_hora_validos , verificar_step
from core.helpers.phone_validation import PhoneValidator
from core.helpers.fluxo import criar_agendamento_e_redirecionar, get_datas_step_client

@require_http_methods(["GET","POST"])
def step_service(request):
    """Etapa de escolha do serviço.
    - GET: exibe os serviços disponíveis.
    - POST: salva o serviço escolhido na sessão e avança para o barbeiro."""
    if request.method == 'POST':
        request.session['service'] = request.POST.get('service')
        return redirect('step_barber')
    return render(request, 'agendamento/step_service.html', {'services': SERVICES, 'back_url': None})

def step_barber(request):
    """Etapa de escolha do barbeiro.
    Requer que um serviço já tenha sido selecionado na sessão.
    - GET: exibe os barbeiros disponíveis.
    - POST: salva o barbeiro escolhido na sessão e avança para a data."""
    verificar_step(request, 'service')
    if request.method == 'POST':
        request.session['barber'] = request.POST.get('barber')
        return redirect('step_date')
    return render(request, 'agendamento/step_barber.html', {'barbers': BARBERS, 'back_url': 'step_service'})

def step_date(request):
    """Etapa de escolha da data.
    Requer que um barbeiro tenha sido selecionado.
    - GET: exibe os próximos 8 dias a partir de hoje.
    - POST: salva a data escolhida na sessão e avança para a escolha de horário."""
    verificar_step(request, 'barber')
    if request.method == 'POST':
        request.session['date'] = request.POST.get('date')
        return redirect('step_hour')
    days = get_future_days()
    return render(request, 'agendamento/step_date.html', {'days': days, 'back_url': 'step_barber'})

def step_hour(request):
    """Etapa de escolha do horário.
    Com base no barbeiro e na data escolhidos, calcula os horários livres
    (exclui horários já ocupados) e permite selecionar um.
    - GET: exibe os horários disponíveis.
    - POST: salva o horário escolhido na sessão e avança para os dados do cliente."""
    verificar_step(request, 'date')
    barber = request.session.get('barber')
    date_str = request.session.get('date')
    day = convert_str_to_date(date_str)
    hours = available_hours_for_day(barber, day)
    if request.method == 'POST':
        request.session['hour'] = request.POST.get('hour')
        return redirect('step_client')
    return render(request, 'agendamento/step_hour.html', {'hours': hours, 'back_url': 'step_date'})

def step_client(request):
    """Etapa de dados do cliente e confirmação.
    Valida as informações (serviço, barbeiro, data e hora), verifica se a hora
    está dentro da janela válida (hoje até 7 dias à frente) e se não está ocupada,
    cria o agendamento (Appointment), limpa a sessão e redireciona para pagamento."""
    verificar_step(request, 'hour')
    if request.method == 'POST':
        data = get_datas_step_client(request)
        if not data:
            return HttpResponseBadRequest()
        client_name, client_phone, service, barber, date_str, hour_str = data
        if not PhoneValidator.is_valid_brazil_number(client_phone):
            return HttpResponseBadRequest()
        day, hr = convert_str_to_day_and_hour(date_str, hour_str)
        if not dia_e_hora_validos(day, hr):
            return HttpResponseBadRequest()
        if horario_ja_ocupado(barber, day, hr):
            return HttpResponseBadRequest()
        return criar_agendamento_e_redirecionar(request, client_name, client_phone, service, barber, day, hr)
    return render(request, 'agendamento/step_client.html', {'back_url': 'step_hour'})


@require_http_methods(["GET"])
def horarios_api(request):
    """API de horários disponíveis.
    Recebe `barber` e `date` via query string e retorna JSON com a lista
    de horários livres no formato HH:MM para o dia informado."""
    barber = request.GET.get('barber')
    date_str = request.GET.get('date')
    return horarios_disponiveis_response(barber, date_str)
