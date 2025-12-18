from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as django_logout
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from scheduling.models import Appointment
from core.helpers.infos import obter_barbers_keys
from core.helpers.fluxo import list_filtered_appointments, get_hours_opts, get_dates_opts
from core.helpers.history import get_past_appointments
from core.helpers.finance import (
    get_paid_appointments, 
    compute_totals,
    calculate_daily_revenue,
    calculate_monthly_revenue,
    calculate_top_services,
    calculate_average_ticket
)
from core.helpers.notifications import (
    format_reschedule_message,
    format_cancel_message,
    send_whatsapp_and_feedback,
    notify_client_change
)
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from django.conf import settings
import os
from core.helpers.appointments import compute_new_hour, apply_hour_shift
from datetime import date, timedelta


class AdminListView(LoginRequiredMixin, View):
    login_url = 'login'
    """Lista agendamentos com filtros por barbeiro, data e hora."""

    def get(self, request):
        # Coleta filtros da querystring
        barber = request.GET.get('barber')
        day = request.GET.get('date')
        hour = request.GET.get('hour')
        # Gera queryset filtrado e opções de data/hora
        qs = list_filtered_appointments(barber, day, hour)
        hours_options = get_hours_opts(qs)
        dates_options = get_dates_opts(qs)
        # Renderiza página com contexto necessário
        return render(request, 'dashboard/admin_list.html', {
            'items': qs,
            'barbers': obter_barbers_keys(),
            'hours_options': hours_options,
            'dates_options': dates_options,
            'today': date.today(),
            'tomorrow': date.today() + timedelta(days=1),
            'is_painel': True,
        })


class AdminDetailView(LoginRequiredMixin, View):
    login_url = 'login'
    """Exibe detalhes de um agendamento específico."""

    def get(self, request, appointment_id):
        # Busca o agendamento ou retorna 404
        ap = get_object_or_404(Appointment, pk=appointment_id)
        # Renderiza a página de detalhes
        return render(request, 'dashboard/admin_detail.html', {'ap': ap, 'is_painel': True})


class AdminHistoryView(LoginRequiredMixin, View):
    login_url = 'login'
    """Lista histórico de agendamentos já passados com filtros opcionais."""

    def get(self, request):
        # Coleta filtros
        barber = request.GET.get('barber')
        start = request.GET.get('start')
        end = request.GET.get('end')
        # Usa helper para montar queryset de histórico
        qs = get_past_appointments(barber=barber, start=start, end=end)
        # Renderiza com barber options para filtro
        return render(request, 'dashboard/admin_history.html', {
            'items': qs,
            'barbers': obter_barbers_keys(),
            'is_painel': True,
        })


class AdminFinanceView(LoginRequiredMixin, View):
    login_url = 'login'
    """Exibe resumo financeiro de agendamentos pagos por método."""

    def get(self, request):
        pagos, virtual, fisico = get_paid_appointments()
        total_virtual, total_fisico = compute_totals(virtual, fisico)
        # Métricas iniciais para gráficos
        today = date.today()
        start_30d = today - timedelta(days=29)
        
        # Receita diária (últimos 30 dias)
        daily_labels, daily_values = calculate_daily_revenue(pagos.filter(date__gte=start_30d))
        
        # Receita mensal (últimos 12 meses)
        start_12m = (today.replace(day=1) - timedelta(days=365))
        monthly_labels, monthly_values = calculate_monthly_revenue(pagos.filter(date__gte=start_12m))
        
        # Top serviços por receita
        service_labels, service_values = calculate_top_services(pagos)
        
        # Ticket médio (últimos 30 dias)
        ticket_medio = calculate_average_ticket(pagos.filter(date__gte=start_30d))

        finance_init = {
            'totais_por_metodo': {
                'labels': ['PIX', 'Dinheiro'],
                'values': [total_virtual, total_fisico],
            },
            'receita_diaria': {
                'labels': daily_labels,
                'values': daily_values,
            },
            'receita_mensal': {
                'labels': monthly_labels,
                'values': monthly_values,
            },
            'top_servicos': {
                'labels': service_labels,
                'values': service_values,
            },
            'ticket_medio': {
                'labels': ['Últimos 30 dias'],
                'values': [round(ticket_medio, 2)],
            },
        }
        return render(request, 'dashboard/admin_finance.html', {
            'pagos': pagos.order_by('-date', '-hour'),
            'total_virtual': total_virtual,
            'total_fisico': total_fisico,
            'finance_init': finance_init,
            'is_painel': True,
        })


class FinanceMetricsApi(LoginRequiredMixin, View):
    login_url = 'login'
    http_method_names = ['get']

    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        metodo = request.GET.get('metodo')
        servico = request.GET.get('servico')
        pagos, virtual, fisico = get_paid_appointments()
        qs = pagos
        # Filtros opcionais
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if metodo in ('pix', 'cash'):
            qs = qs.filter(payment_method=metodo)
        if servico in ('barba', 'cabelo', 'combo'):
            qs = qs.filter(service=servico)
        
        # Recalcula métricas com base no filtro
        # Totais por método
        v_qs = qs.filter(payment_method='pix')
        f_qs = qs.filter(payment_method='cash')
        total_virtual, total_fisico = compute_totals(v_qs, f_qs)
        
        # Receita diária
        daily_labels, daily_values = calculate_daily_revenue(qs)
        
        # Receita mensal
        monthly_labels, monthly_values = calculate_monthly_revenue(qs)
        
        # Top serviços
        service_labels, service_values = calculate_top_services(qs)
        
        # Ticket médio
        ticket_medio = calculate_average_ticket(qs)

        return JsonResponse({
            'totais_por_metodo': {
                'labels': ['PIX', 'Dinheiro'],
                'values': [total_virtual, total_fisico],
            },
            'receita_diaria': {
                'labels': daily_labels,
                'values': daily_values,
            },
            'receita_mensal': {
                'labels': monthly_labels,
                'values': monthly_values,
            },
            'top_servicos': {
                'labels': service_labels,
                'values': service_values,
            },
            'ticket_medio': {
                'labels': ['Período selecionado'],
                'values': [round(ticket_medio, 2)],
            },
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


class AdminShiftHourView(LoginRequiredMixin, View):
    login_url = 'login'
    http_method_names = ['post']
    """Move o horário de um agendamento em 1 hora para trás/à frente."""

    def post(self, request, appointment_id, direction):
        # Recupera o agendamento pelo ID ou 404
        ap = get_object_or_404(Appointment, pk=appointment_id)
        # Calcula/valida nova hora usando helper
        new_hour, error_code = compute_new_hour(ap, direction)
        if error_code == 'invalid_direction':
            messages.error(request, 'Direção inválida para mover horário')
            return redirect('admin_detail', appointment_id=ap.id)
        if error_code == 'invalid_slot':
            messages.error(request, 'Horário inválido para o dia selecionado')
            return redirect('admin_detail', appointment_id=ap.id)
        if error_code == 'occupied':
            messages.error(request, 'Não foi possível mover: horário já ocupado')
            return redirect('admin_detail', appointment_id=ap.id)
        # Aplica atualização na hora e marca como reagendado
        apply_hour_shift(ap, new_hour)
        # Notifica cliente via WhatsApp
        text = format_reschedule_message(ap, new_hour)
        notify_client_change(request, ap, text)
        
        # Feedback de sucesso e redireciona
        messages.success(request, 'Agendamento movido com sucesso')
        return redirect('admin_detail', appointment_id=ap.id)


class AdminConfirmCashView(LoginRequiredMixin, View):
    login_url = 'login'
    http_method_names = ['post']
    """Confirma pagamento em dinheiro para um agendamento."""

    def post(self, request, appointment_id):
        # Busca o agendamento ou 404
        ap = get_object_or_404(Appointment, pk=appointment_id)
        # Confirma pagamento somente quando método/estado compatíveis
        if ap.payment_method == 'cash' and ap.payment_status != 'pago':
            ap.payment_status = 'pago'
            ap.save(update_fields=['payment_status'])
        # Redireciona para detalhes
        return redirect('admin_detail', appointment_id=ap.id)


class WhatsAppSendView(View):
    http_method_names = ['post']
    """Endpoint para envio genérico de mensagem WhatsApp."""

    def post(self, request):
        # Valida parâmetros obrigatórios
        number = request.POST.get("number")
        text = request.POST.get("text")
        if not number or not text:
            return JsonResponse(
                {"ok": False, "error": "missing_params", "details": "Parâmetros 'number' e 'text' são obrigatórios"},
                status=400
            )
        # Envia mensagem e responde com status adequado
        result = send_mensage(number, text)
        if result.get("ok"):
            return JsonResponse(result, status=200)
        return JsonResponse(result, status=400)


class AdminCancelAppointmentView(LoginRequiredMixin, View):
    login_url = 'login'
    http_method_names = ['post']
    """Cancela um agendamento e notifica o cliente via WhatsApp."""

    def post(self, request, appointment_id):
        # Recupera agendamento ou 404
        ap = get_object_or_404(Appointment, pk=appointment_id)
        # Evita cancelamento duplicado
        if ap.status != 'ativo':
            messages.warning(request, 'Agendamento já está cancelado')
            return redirect('admin_detail', appointment_id=ap.id)
        # Atualiza campos de cancelamento
        reason = request.POST.get('reason') or ''
        ap.status = 'cancelado'
        ap.cancelled_by = 'barber'
        ap.cancelled_at = timezone.now()
        ap.cancel_reason = reason
        ap.save(update_fields=['status', 'cancelled_by', 'cancelled_at', 'cancel_reason'])
        # Notifica cliente via WhatsApp
        text = format_cancel_message(ap, reason)
        notify_client_change(request, ap, text)
        
        # Feedback de sucesso e redireciona
        messages.success(request, 'Agendamento cancelado com sucesso')
        return redirect('admin_detail', appointment_id=ap.id)

# Mapeia nomes antigos para class-based views, mantendo compatibilidade com urls
admin_list = AdminListView.as_view()
admin_detail = AdminDetailView.as_view()
admin_history = AdminHistoryView.as_view()
admin_finance = AdminFinanceView.as_view()
admin_shift_hour = AdminShiftHourView.as_view()
admin_confirm_cash = AdminConfirmCashView.as_view()
whatsapp_send = WhatsAppSendView.as_view()
admin_cancel_appointment = AdminCancelAppointmentView.as_view()


class AdminProfileView(LoginRequiredMixin, View):
    login_url = 'login'
    """Perfil do administrador: aparência, foto e segurança."""

    def get(self, request):
        return render(request, 'dashboard/admin_profile.html', {
            'is_painel': True,
        })

    def post(self, request):
        form_type = request.POST.get('form_type')
        if form_type == 'appearance':
            theme = request.POST.get('theme_name') or 'theme-green'
            if hasattr(request.user, 'theme_name'):
                request.user.theme_name = theme
                request.user.save(update_fields=['theme_name'])
            messages.success(request, 'Tema atualizado')
            return redirect('admin_profile')
        elif form_type == 'password':
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha atualizada com sucesso')
                return redirect('admin_profile')
            for field, errs in form.errors.items():
                for e in errs:
                    messages.error(request, f'{e}')
            return redirect('admin_profile')
        elif form_type == 'avatar':
            image_file = request.FILES.get('avatar')
            try:
                x = float(request.POST.get('crop_x', '0') or '0')
                y = float(request.POST.get('crop_y', '0') or '0')
                w = float(request.POST.get('crop_w', '0') or '0')
                h = float(request.POST.get('crop_h', '0') or '0')
            except ValueError:
                x = y = w = h = 0
            if not image_file:
                messages.error(request, 'Nenhuma imagem enviada')
                return redirect('admin_profile')
            try:
                ctype = getattr(image_file, 'content_type', '') or ''
                if ctype not in ('image/png', 'image/jpeg', 'image/jpg'):
                    messages.error(request, 'Formato inválido. Envie PNG ou JPEG.')
                    return redirect('admin_profile')
                img = Image.open(image_file)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                ow, oh = img.size
                if ow < 96 or oh < 96:
                    messages.error(request, 'Imagem muito pequena. Mínimo 96×96 px.')
                    return redirect('admin_profile')
                if w <= 0 or h <= 0:
                    side = min(ow, oh)
                    x = (ow - side) / 2
                    y = (oh - side) / 2
                    w = h = side
                box = (max(0, int(x)), max(0, int(y)), min(ow, int(x + w)), min(oh, int(y + h)))
                cropped = img.crop(box)
                final = cropped.resize((96, 96), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                final.save(buffer, format='PNG', optimize=True)
                buffer.seek(0)
                filename = f'avatar_user_{request.user.id}.png'
                request.user.avatar.save(filename, ContentFile(buffer.read()), save=True)
                messages.success(request, 'Foto de perfil atualizada')
            except Exception:
                messages.error(request, 'Falha ao processar a imagem. Tente outro arquivo.')
            return redirect('admin_profile')
        messages.error(request, 'Ação inválida')
        return redirect('admin_profile')

admin_profile = AdminProfileView.as_view()
