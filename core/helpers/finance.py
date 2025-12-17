from scheduling.models import Appointment


def get_paid_appointments():
    """Retorna conjuntos de agendamentos pagos e separados por método.
    
    - pagos: todos com status 'pago'
    - virtual: pagos via 'pix'
    - fisico: pagos em 'cash'
    """
    # Recupera todos e filtra por pagos
    all_qs = Appointment.objects.all()
    pagos = all_qs.filter(payment_status='pago')
    # Separa por método de pagamento
    virtual = pagos.filter(payment_method='pix')
    fisico = pagos.filter(payment_method='cash')
    return pagos, virtual, fisico


def compute_totals(virtual_qs, fisico_qs):
    """Calcula totais em reais a partir dos serviços.
    
    - combo: 100
    - demais: 50
    """
    # Soma valores com base no tipo de serviço
    total_virtual = sum(100 if ap.service == 'combo' else 50 for ap in virtual_qs)
    total_fisico = sum(100 if ap.service == 'combo' else 50 for ap in fisico_qs)
    return total_virtual, total_fisico


def calculate_daily_revenue(queryset):
    """Calcula receita diária baseada no queryset fornecido.
    
    Retorna:
        labels: lista de datas (strings)
        values: lista de valores correspondentes
    """
    daily_map = {}
    for ap in queryset.order_by('date'):
        key = ap.date.strftime('%Y-%m-%d')
        daily_map[key] = daily_map.get(key, 0) + ap.price()
    labels = sorted(daily_map.keys())
    values = [daily_map[k] for k in labels]
    return labels, values


def calculate_monthly_revenue(queryset):
    """Calcula receita mensal baseada no queryset fornecido.
    
    Retorna:
        labels: lista de meses (YYYY-MM)
        values: lista de valores correspondentes
    """
    monthly_map = {}
    for ap in queryset.order_by('date'):
        key = f"{ap.date.year}-{ap.date.month:02d}"
        monthly_map[key] = monthly_map.get(key, 0) + ap.price()
    labels = sorted(monthly_map.keys())
    values = [monthly_map[k] for k in labels]
    return labels, values


def calculate_top_services(queryset):
    """Calcula receita por serviço.
    
    Retorna:
        labels: ['barba', 'cabelo', 'combo']
        values: valores correspondentes
    """
    service_map = {'barba': 0, 'cabelo': 0, 'combo': 0}
    for ap in queryset:
        service_map[ap.service] = service_map.get(ap.service, 0) + ap.price()
    labels = ['barba', 'cabelo', 'combo']
    values = [service_map[s] for s in labels]
    return labels, values


def calculate_average_ticket(queryset):
    """Calcula ticket médio do queryset.
    
    Retorna:
        float: valor do ticket médio
    """
    count = queryset.count()
    total = sum(ap.price() for ap in queryset)
    return (total / count) if count else 0
