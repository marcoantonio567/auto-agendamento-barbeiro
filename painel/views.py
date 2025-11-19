from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from agendamento.models import Appointment
from barbearia.helpers.infos import BARBERS


@login_required(login_url='login')
def admin_list(request):
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
    ap = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, 'agendamento/admin_detail.html', {'ap': ap})


def login_view(request):
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
    logout(request)
    return redirect('login')