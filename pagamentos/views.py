from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.core.signing import Signer, BadSignature
from agendamento.models import Appointment


def pagamento(request, sid):
    signer = Signer()
    try:
        ap_id = signer.unsign(sid)
    except BadSignature:
        raise Http404
    ap = get_object_or_404(Appointment, pk=ap_id)
    return render(request, 'agendamento/pagamento.html', {'ap': ap, 'sid': sid})


@require_http_methods(["POST"])
def pagamento_confirmar(request, sid):
    signer = Signer()
    try:
        ap_id = signer.unsign(sid)
    except BadSignature:
        raise Http404
    ap = get_object_or_404(Appointment, pk=ap_id)
    ap.payment_status = 'pago'
    ap.save()
    return redirect('pagamento', sid=sid)


@require_http_methods(["POST"])
def pagamento_falhar(request, sid):
    signer = Signer()
    try:
        ap_id = signer.unsign(sid)
    except BadSignature:
        raise Http404
    ap = get_object_or_404(Appointment, pk=ap_id)
    ap.payment_status = 'falhou'
    ap.save()
    return redirect('pagamento', sid=sid)