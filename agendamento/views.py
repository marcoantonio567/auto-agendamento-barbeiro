from datetime import date as ddate, datetime, time, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import Appointment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from agendamento.helpers.infos import SERVICES, BARBERS
from agendamento.helpers.datas import sete_dias_futuros, converter_str_para_date, converter_str_para_day_e_hora, json_horarios_vazio
from agendamento.helpers.disponibilidade import available_hours_for_day, horario_ja_ocupado, horarios_disponiveis_response
from agendamento.helpers.validacao import dia_e_hora_validos , verificar_step
from agendamento.helpers.fluxo import criar_agendamento_e_redirecionar, obter_dados_step_client

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
    days = sete_dias_futuros()
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
    day = converter_str_para_date(date_str)
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
        data = obter_dados_step_client(request)
        if not data:
            return HttpResponseBadRequest()
        client_name, service, barber, date_str, hour_str = data
        day, hr = converter_str_para_day_e_hora(date_str, hour_str)
        if not dia_e_hora_validos(day, hr):
            return HttpResponseBadRequest()
        if horario_ja_ocupado(barber, day, hr):
            return HttpResponseBadRequest()
        return criar_agendamento_e_redirecionar(request, client_name, service, barber, day, hr)
    return render(request, 'agendamento/step_client.html', {'back_url': 'step_hour'})


@require_http_methods(["GET"])
def horarios_api(request):
    """API de horários disponíveis.
    Recebe `barber` e `date` via query string e retorna JSON com a lista
    de horários livres no formato HH:MM para o dia informado."""
    barber = request.GET.get('barber')
    date_str = request.GET.get('date')
    return horarios_disponiveis_response(barber, date_str)


def pagamento(request, appointment_id):
    """Exibe a página de pagamento para o agendamento informado."""
    ap = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, 'agendamento/pagamento.html', {'ap': ap})


@require_http_methods(["POST"])
def pagamento_confirmar(request, appointment_id):
    """Marca o agendamento como pago e redireciona para a tela de pagamento."""
    ap = get_object_or_404(Appointment, pk=appointment_id)
    ap.payment_status = 'pago'
    ap.save()
    return redirect('pagamento', appointment_id=ap.id)


@require_http_methods(["POST"])
def pagamento_falhar(request, appointment_id):
    """Marca o agendamento como falhou e redireciona para a tela de pagamento."""
    ap = get_object_or_404(Appointment, pk=appointment_id)
    ap.payment_status = 'falhou'
    ap.save()
    return redirect('pagamento', appointment_id=ap.id)


@login_required(login_url='login')
def admin_list(request):
    """Lista os agendamentos com filtros opcionais por barbeiro, data e hora.
    Requer usuário autenticado."""
    qs = Appointment.objects.all().order_by('date', 'hour', 'barber')
    barber = request.GET.get('barber')
    day = request.GET.get('date')
    hour = request.GET.get('hour')
    if barber:
        qs = qs.filter(barber=barber)
    if day:
        try:
            d = datetime.strptime(day, '%Y-%m-%d').date()
            qs = qs.filter(date=d)
        except ValueError:
            pass
    if hour:
        try:
            h = datetime.strptime(hour, '%H:%M').time()
            qs = qs.filter(hour=h)
        except ValueError:
            pass
    return render(request, 'agendamento/admin_list.html', {
        'items': qs,
        'barbers': [b['key'] for b in BARBERS],
    })


@login_required(login_url='login')
def admin_detail(request, appointment_id):
    """Exibe os detalhes de um agendamento específico.
    Requer usuário autenticado."""
    ap = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, 'agendamento/admin_detail.html', {'ap': ap})

def login_view(request):
    """Tela de login e autenticação.
    - POST: autentica o usuário e redireciona para `next` (ou lista admin).
    - GET: se já autenticado, vai para a lista; caso contrário, exibe o formulário."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or 'admin_list'
            return redirect(next_url)
        return render(request, 'agendamento/login.html', {'error': 'Credenciais inválidas'})
    if request.user.is_authenticated:
        return redirect('admin_list')
    return render(request, 'agendamento/login.html')


def logout_view(request):
    """Finaliza a sessão do usuário e redireciona para a página de login."""
    logout(request)
    return redirect('login')