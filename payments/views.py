from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from core.helpers.fluxo import get_appointment_by_sid_or_404


@require_http_methods(["GET"])
def pagamento(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    return render(request, 'payments/pagamento.html', {'ap': ap, 'sid': sid})


@require_http_methods(["POST"])
def pagamento_confirmar(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    ap.payment_status = 'pago'
    ap.save(update_fields=["payment_status"])
    return redirect('pagamento', sid=sid)


@require_http_methods(["POST"])
def pagamento_falhar(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    ap.payment_status = 'falhou'
    ap.save(update_fields=["payment_status"])
    return redirect('pagamento', sid=sid)
