from datetime import date as ddate, datetime, time, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Appointment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


SERVICES = [
    {
        'key': 'barba',
        'label': 'Fazer a barba',
        'price': 50,
        'icon': 'moustache',
        'description': 'Linhas precisas e acabamento quente para realçar o rosto.',
    },
    {
        'key': 'cabelo',
        'label': 'Cortar o cabelo',
        'price': 50,
        'icon': 'comb',
        'description': 'Corte clássico ou moderno com finalização profissional.',
    },
    {
        'key': 'combo',
        'label': 'Barba + cabelo',
        'price': 100,
        'icon': 'sparkles',
        'description': 'Pacote completo para sair renovado do totem.',
    },
]
BARBERS = [
    {
        'key': 'Japa',
        'name': 'Japa',
        'photo': '/static/img/barbers/japa.svg',
    },
    {
        'key': 'João',
        'name': 'João',
        'photo': '/static/img/barbers/joao.svg',
    },
    {
        'key': 'Marco',
        'name': 'Marco',
        'photo': '/static/img/barbers/marco.svg',
    },
    {
        'key': 'Daniel',
        'name': 'Daniel',
        'photo': '/static/img/barbers/daniel.svg',
    },
]


def slots_for_day(dt):
    slots = []
    for h in range(7, 19):
        slots.append(time(hour=h, minute=0))
    return slots


def index(request):
    return redirect('step_service')

def step_service(request):
    if request.method == 'POST':
        request.session['service'] = request.POST.get('service')
        return redirect('step_barber')
    return render(request, 'agendamento/step_service.html', {'services': SERVICES, 'back_url': None})

def step_barber(request):
    if not request.session.get('service'):
        return redirect('step_service')
    if request.method == 'POST':
        request.session['barber'] = request.POST.get('barber')
        return redirect('step_date')
    return render(request, 'agendamento/step_barber.html', {'barbers': BARBERS, 'back_url': 'step_service'})

def step_date(request):
    if not request.session.get('barber'):
        return redirect('step_barber')
    if request.method == 'POST':
        request.session['date'] = request.POST.get('date')
        return redirect('step_hour')
    days = [(ddate.today() + timedelta(days=i)) for i in range(0, 8)]
    return render(request, 'agendamento/step_date.html', {'days': days, 'back_url': 'step_barber'})

def step_hour(request):
    if not request.session.get('date'):
        return redirect('step_date')
    barber = request.session.get('barber')
    date_str = request.session.get('date')
    day = datetime.strptime(date_str, '%Y-%m-%d').date()
    taken = set(Appointment.objects.filter(barber=barber, date=day).values_list('hour', flat=True))
    hours = []
    for hr in slots_for_day(day):
        if hr not in taken:
            hours.append(hr.strftime('%H:%M'))
    if request.method == 'POST':
        request.session['hour'] = request.POST.get('hour')
        return redirect('step_client')
    return render(request, 'agendamento/step_hour.html', {'hours': hours, 'back_url': 'step_date'})

def step_client(request):
    if not request.session.get('hour'):
        return redirect('step_hour')
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        service = request.session.get('service')
        barber = request.session.get('barber')
        date_str = request.session.get('date')
        hour_str = request.session.get('hour')
        if not all([client_name, service, barber, date_str, hour_str]):
            return HttpResponseBadRequest()
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
            hr = datetime.strptime(hour_str, '%H:%M').time()
        except ValueError:
            return HttpResponseBadRequest()
        today = ddate.today()
        if day < today or day > today + timedelta(days=7):
            return HttpResponseBadRequest()
        if hr not in slots_for_day(day):
            return HttpResponseBadRequest()
        exists = Appointment.objects.filter(barber=barber, date=day, hour=hr).exists()
        if exists:
            return HttpResponseBadRequest()
        ap = Appointment.objects.create(client_name=client_name, service=service, barber=barber, date=day, hour=hr)
        request.session.flush()
        return redirect('pagamento', appointment_id=ap.id)
    return render(request, 'agendamento/step_client.html', {'back_url': 'step_hour'})


@require_http_methods(["GET"])
def horarios_api(request):
    barber = request.GET.get('barber')
    date_str = request.GET.get('date')
    if not barber or not date_str:
        return JsonResponse({'hours': []})
    try:
        day = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'hours': []})
    taken = set(Appointment.objects.filter(barber=barber, date=day).values_list('hour', flat=True))
    hours = []
    for hr in slots_for_day(day):
        if hr not in taken:
            hours.append(hr.strftime('%H:%M'))
    return JsonResponse({'hours': hours})


def pagamento(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    return render(request, 'agendamento/pagamento.html', {'ap': ap})


@require_http_methods(["POST"])
def pagamento_confirmar(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    ap.payment_status = 'pago'
    ap.save()
    return redirect('pagamento', appointment_id=ap.id)


@require_http_methods(["POST"])
def pagamento_falhar(request, appointment_id):
    ap = get_object_or_404(Appointment, pk=appointment_id)
    ap.payment_status = 'falhou'
    ap.save()
    return redirect('pagamento', appointment_id=ap.id)


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