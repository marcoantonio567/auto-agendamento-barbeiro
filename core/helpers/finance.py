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

