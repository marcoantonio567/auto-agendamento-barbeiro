from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from agendamento.models import Appointment
from barbearia.helpers.infos import obter_barbers_keys
from barbearia.helpers.fluxo import listar_agendamentos_filtrados
from datetime import date, timedelta, datetime
from django.db.models import Q
from django.contrib import messages
from barbearia.helpers.disponibilidade import horario_ja_ocupado
from barbearia.helpers.validacao import get_hours_delta_from_direction
from barbearia.helpers.datas import shift_hour_by_delta
from barbearia.helpers.slots import is_valid_slot_for_day
from barbearia.helpers.phone_validation import PhoneValidator
from whastsapp_api import send_mensage


@login_required(login_url='login')
def admin_list(request):
    barber = request.GET.get('barber')
    day = request.GET.get('date')
    hour = request.GET.get('hour')
    qs = listar_agendamentos_filtrados(barber, day, hour)
    hours_opts = sorted({h.hour for h in qs.values_list('hour', flat=True)})
    dates_opts = list(qs.order_by('date').values_list('date', flat=True).distinct())
    return render(request, 'dashboard/admin_list.html', {
        'items': qs,
        'barbers': obter_barbers_keys(),
        'hours_options': hours_opts,
        'dates_options': dates_opts,
        'today': date.today(),
        'tomorrow': date.today() + timedelta(days=1),
        'is_painel': True,
    })


@login_required(login_url='login')
def admin_detail(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, 'dashboard/admin_detail.html', {'ap': ap, 'is_painel': True})


@login_required(login_url='login')
def admin_history(request):
    barber = request.GET.get('barber')
    start = request.GET.get('start')
    end = request.GET.get('end')
    today = date.today()
    now_time = datetime.now().time()
    qs = Appointment.objects.filter(Q(date__lt=today) | Q(date=today, hour__lt=now_time))
    if barber:
        qs = qs.filter(barber=barber)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    qs = qs.order_by('-date', '-hour')
    return render(request, 'dashboard/admin_history.html', {
        'items': qs,
        'barbers': obter_barbers_keys(),
        'is_painel': True,
    })


@login_required(login_url='login')
def admin_finance(request):
    all_qs = Appointment.objects.all()
    pagos = all_qs.filter(payment_status='pago')
    pendentes = all_qs.filter(payment_status='pendente')
    falhos = all_qs.filter(payment_status='falhou')
    total_pago = sum(100 if ap.service == 'combo' else 50 for ap in pagos)
    total_pendente = sum(100 if ap.service == 'combo' else 50 for ap in pendentes)
    total_falhou = sum(100 if ap.service == 'combo' else 50 for ap in falhos)
    return render(request, 'dashboard/admin_finance.html', {
        'pagos': pagos.order_by('-date', '-hour'),
        'total_pago': total_pago,
        'total_pendente': total_pendente,
        'total_falhou': total_falhou,
        'is_painel': True,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            remember = request.POST.get('remember')
            if remember == 'on':
                request.session.set_expiry(60*60*24*30)
            else:
                request.session.set_expiry(0)
            next_url = request.GET.get('next') or 'admin_list'
            return redirect(next_url)
        return render(request, 'dashboard/login.html', {'error': 'Credenciais inválidas'})
    if request.user.is_authenticated:
        return redirect('admin_list')
    return render(request, 'dashboard/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def admin_shift_hour(request, appointment_id, direction):
    """Move o horário de um agendamento em 1 hora para trás ou para frente.

    - direction: 'prev' (voltar 1h) ou 'next' (avançar 1h)
    - valida se a nova hora está nos slots do dia e se não há conflito
    - atualiza somente os campos necessários e informa feedback ao usuário
    """

    # Recupera o agendamento pelo ID ou retorna 404 se não existir
    ap = get_object_or_404(Appointment, pk=appointment_id)

    # Valida a direção informada usando helper; retorna None se inválida
    hours_delta = get_hours_delta_from_direction(direction)
    if hours_delta is None:
        messages.error(request, 'Direção inválida para mover horário')
        return redirect('admin_detail', appointment_id=ap.id)

    # Calcula a nova hora somando/subtraindo 1h da hora atual do agendamento
    new_hour = shift_hour_by_delta(ap.date, ap.hour, hours_delta)

    # Bloqueia se a nova hora não faz parte dos slots válidos do dia
    if not is_valid_slot_for_day(ap.date, new_hour):
        messages.error(request, 'Horário inválido para o dia selecionado')
        return redirect('admin_detail', appointment_id=ap.id)

    # Bloqueia se a nova hora já está ocupada para o barbeiro
    if horario_ja_ocupado(ap.barber, ap.date, new_hour):
        messages.error(request, 'Não foi possível mover: horário já ocupado')
        return redirect('admin_detail', appointment_id=ap.id)

    # Atualiza a hora do agendamento e marca como reagendado
    ap.hour = new_hour
    ap.rescheduled = True
    # Salva apenas os campos modificados para eficiência
    ap.save(update_fields=['hour', 'rescheduled'])

    # Envia mensagem ao cliente informando o novo horário
    try:
        phone_digits = PhoneValidator.extract_digits(ap.client_phone)
        if phone_digits and len(phone_digits) == 10:
            
            date_str = ap.date.strftime('%d/%m/%Y')
            hour_str = new_hour.strftime('%H:%M')
            text = f"Olá, {ap.client_name}! Seu horário com {ap.barber} foi alterado para {date_str} às {hour_str}."
            send_mensage(phone_digits, text)
    except Exception:
        pass

    # Informa sucesso e retorna para a página de detalhes
    messages.success(request, 'Agendamento movido com sucesso')
    return redirect('admin_detail', appointment_id=ap.id)
