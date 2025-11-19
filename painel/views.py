from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from agendamento.models import Appointment
from barbearia.helpers.infos import obter_barbers_keys
from barbearia.helpers.fluxo import listar_agendamentos_filtrados


@login_required(login_url='login')
def admin_list(request):
    barber = request.GET.get('barber')
    day = request.GET.get('date')
    hour = request.GET.get('hour')
    qs = listar_agendamentos_filtrados(barber, day, hour)
    return render(request, 'painel/admin_list.html', {
        'items': qs,
        'barbers': obter_barbers_keys(),
    })


@login_required(login_url='login')
def admin_detail(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, 'painel/admin_detail.html', {'ap': ap})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or 'admin_list'
            return redirect(next_url)
        return render(request, 'painel/login.html', {'error': 'Credenciais inválidas'})
    if request.user.is_authenticated:
        return redirect('admin_list')
    return render(request, 'painel/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')