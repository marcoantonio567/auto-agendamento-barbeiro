from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from agendamento.models import Appointment


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