from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from agendamento.models import Appointment
from barbearia.helpers.infos import obter_barbers_keys
from barbearia.helpers.fluxo import listar_agendamentos_filtrados
from datetime import date, timedelta


@login_required(login_url='login')
def admin_list(request):
    barber = request.GET.get('barber')
    day = request.GET.get('date')
    hour = request.GET.get('hour')
    qs = listar_agendamentos_filtrados(barber, day, hour)
    hours_opts = sorted({h.hour for h in qs.values_list('hour', flat=True)})
    dates_opts = list(qs.order_by('date').values_list('date', flat=True).distinct())
    return render(request, 'painel/admin_list.html', {
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
    return render(request, 'painel/admin_detail.html', {'ap': ap, 'is_painel': True})


@login_required(login_url='login')
def admin_history(request):
    barber = request.GET.get('barber')
    start = request.GET.get('start')
    end = request.GET.get('end')
    qs = Appointment.objects.all()
    if barber:
        qs = qs.filter(barber=barber)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    qs = qs.order_by('-date', '-hour')
    return render(request, 'painel/admin_history.html', {
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
    return render(request, 'painel/admin_finance.html', {
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
        return render(request, 'painel/login.html', {'error': 'Credenciais inválidas'})
    if request.user.is_authenticated:
        return redirect('admin_list')
    return render(request, 'painel/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')