from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as django_logout
from django.views import View
from django.http import JsonResponse
from scheduling.models import Appointment
from core.helpers.infos import obter_barbers_keys
from django.views.decorators.http import require_http_methods
from core.helpers.fluxo import list_filtered_appointments, get_hours_opts, get_dates_opts
from datetime import date, timedelta, datetime
from django.db.models import Q
from django.contrib import messages
from core.helpers.disponibilidade import horario_ja_ocupado
from core.helpers.validacao import get_hours_delta_from_direction
from core.helpers.datas import shift_hour_by_delta
from core.helpers.slots import is_valid_slot_for_day
from core.helpers.phone_validation import PhoneValidator
from whastsapp_api import send_mensage
from django.utils import timezone


@login_required(login_url='login')
def admin_list(request):
    barber = request.GET.get('barber')
    day = request.GET.get('date')
    hour = request.GET.get('hour')
    qs = list_filtered_appointments(barber, day, hour)
    hours_opts = get_hours_opts(qs)
    dates_opts = get_dates_opts(qs)
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
    virtual = pagos.filter(payment_method='pix')
    fisico = pagos.filter(payment_method='cash')
    total_virtual = sum(100 if ap.service == 'combo' else 50 for ap in virtual)
    total_fisico = sum(100 if ap.service == 'combo' else 50 for ap in fisico)
    return render(request, 'dashboard/admin_finance.html', {
        'pagos': pagos.order_by('-date', '-hour'),
        'total_virtual': total_virtual,
        'total_fisico': total_fisico,
        'is_painel': True,
    })


class LoginView(View):
    # Exibe o formulário de login ou redireciona se já autenticado
    def get(self, request):
        if self._is_authenticated(request):
            return redirect('admin_list')
        return self._render_login(request)

    # Processa o envio do formulário de login
    def post(self, request):
        username, password = self._extract_credentials(request)
        user = self._authenticate_user(request, username, password)
        if user:
            self._login_user(request, user)
            self._apply_remember_me(request)
            return self._redirect_next(request)
        return self._render_login(request, error='Credenciais inválidas')

    # Verifica se o usuário já está autenticado
    def _is_authenticated(self, request):
        return request.user.is_authenticated

    # Extrai credenciais do POST
    def _extract_credentials(self, request):
        return request.POST.get('username'), request.POST.get('password')

    # Tenta autenticar o usuário com Django
    def _authenticate_user(self, request, username, password):
        return authenticate(request, username=username, password=password)

    # Realiza o login do usuário
    def _login_user(self, request, user):
        login(request, user)

    # Ajusta o tempo de expiração da sessão conforme "remember"
    def _apply_remember_me(self, request):
        remember = request.POST.get('remember')
        if remember == 'on':
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30 dias
        else:
            request.session.set_expiry(0)  # expira ao fechar o navegador

    # Redireciona para a próxima URL ou para o dashboard
    def _redirect_next(self, request):
        next_url = request.GET.get('next') or 'admin_list'
        return redirect(next_url)

    # Renderiza a página de login com possível erro
    def _render_login(self, request, error=None):
        context = {'error': error} if error else {}
        return render(request, 'dashboard/login.html', context)


    # Efetua logout e redireciona para a página de login
    @staticmethod
    def logout(request):
        django_logout(request)
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

    # Envia mensagem ao cliente informando o novo horário e exibe feedback
    phone_digits = PhoneValidator.extract_digits(ap.client_phone)
    if not phone_digits or len(phone_digits) != 10:
        messages.warning(request, 'Telefone do cliente inválido para envio de WhatsApp')
    else:
        date_str = ap.date.strftime('%d/%m/%Y')
        hour_str = new_hour.strftime('%H:%M')
        text = f"Olá, {ap.client_name}! Seu horário com {ap.barber} foi alterado para {date_str} às {hour_str}."
        result = send_mensage(phone_digits, text)
        if not result.get('ok'):
            err = result.get('error') or 'erro_desconhecido'
            details = result.get('details')
            if details:
                messages.error(request, f'Falha ao enviar WhatsApp: {err} ({details})')
            else:
                messages.error(request, f'Falha ao enviar WhatsApp: {err}')
        else:
            messages.success(request, 'WhatsApp enviado ao cliente')

    # Informa sucesso e retorna para a página de detalhes
    messages.success(request, 'Agendamento movido com sucesso')
    return redirect('admin_detail', appointment_id=ap.id)


@login_required(login_url='login')
@require_http_methods(["POST"])
def admin_confirm_cash(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    if ap.payment_method == 'cash' and ap.payment_status != 'pago':
        ap.payment_status = 'pago'
        ap.save(update_fields=['payment_status'])
    return redirect('admin_detail', appointment_id=ap.id)


@require_http_methods(["POST"])
def whatsapp_send(request):
    number = request.POST.get("number")
    text = request.POST.get("text")
    if not number or not text:
        return JsonResponse(
            {"ok": False, "error": "missing_params", "details": "Parâmetros 'number' e 'text' são obrigatórios"},
            status=400
        )
    result = send_mensage(number, text)
    if result.get("ok"):
        return JsonResponse(result, status=200)
    return JsonResponse(result, status=400)


@login_required(login_url='login')
@require_http_methods(["POST"])
def admin_cancel_appointment(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    if ap.status != 'ativo':
        messages.warning(request, 'Agendamento já está cancelado')
        return redirect('admin_detail', appointment_id=ap.id)
    reason = request.POST.get('reason') or ''
    ap.status = 'cancelado'
    ap.cancelled_by = 'barber'
    ap.cancelled_at = timezone.now()
    ap.cancel_reason = reason
    ap.save(update_fields=['status', 'cancelled_by', 'cancelled_at', 'cancel_reason'])
    phone_digits = PhoneValidator.extract_digits(ap.client_phone)
    if phone_digits and len(phone_digits) == 10:
        date_str = ap.date.strftime('%d/%m/%Y')
        hour_str = ap.hour.strftime('%H:%M')
        base_text = f"Olá, {ap.client_name}! Seu horário com {ap.barber} em {date_str} às {hour_str} foi cancelado pelo barbeiro."
        if reason:
            base_text += f" Motivo: {reason}."
        base_text += " Se desejar, responda para remarcar."
        result = send_mensage(phone_digits, base_text)
        if result.get('ok'):
            messages.success(request, 'WhatsApp enviado ao cliente informando cancelamento')
        else:
            err = result.get('error') or 'erro_desconhecido'
            details = result.get('details')
            if details:
                messages.error(request, f'Falha ao enviar WhatsApp: {err} ({details})')
            else:
                messages.error(request, f'Falha ao enviar WhatsApp: {err}')
    else:
        messages.warning(request, 'Telefone do cliente inválido para envio de WhatsApp')
    messages.success(request, 'Agendamento cancelado com sucesso')
    return redirect('admin_detail', appointment_id=ap.id)
