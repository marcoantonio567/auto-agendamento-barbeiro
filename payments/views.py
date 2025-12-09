from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from core.helpers.fluxo import get_appointment_by_sid_or_404
from payments.services import get_abacate_pay_service
from django.http import JsonResponse


@require_http_methods(["GET"])
def pagamento(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    if ap.payment_status == 'pago':
        try:
            del request.session[f"qr_{sid}"]
        except Exception:
            pass
        return redirect('pagamento_sucesso', sid=sid)
    print("[pagamento] sid:", sid)
    print("[pagamento] service:", ap.service, "price:", ap.price())
    print("[pagamento] client:", ap.client_name, "phone:", ap.client_phone)
    print("[pagamento] barber:", ap.barber, "date:", ap.date, "hour:", ap.hour)
    qr = request.session.get(f"qr_{sid}") or {"ok": False}
    resp = render(request, 'payments/pagamento.html', {'ap': ap, 'sid': sid, 'qr': qr})
    resp['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp['Pragma'] = 'no-cache'
    return resp


@require_http_methods(["POST"])
def pagamento_confirmar(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    print("[pagamento_confirmar] sid:", sid)
    print("[pagamento_confirmar] current_status:", ap.payment_status)
    svc = get_abacate_pay_service()
    desc = f"Agendamento {ap.service_label()} - {ap.client_name}"
    qr = svc.gerar_qrcode(amount=ap.price(), description=desc, metadata={"sid": sid})
    print("[pagamento_confirmar] qr_ok:", qr.get("ok"))
    if not qr.get("ok"):
        print("[pagamento_confirmar] qr_error:", qr.get("error"))
    else:
        print("[pagamento_confirmar] charge_id:", qr.get("charge_id"))
        print("[pagamento_confirmar] has_qr_image:", bool(qr.get("qr_code_image_base64")))
        print("[pagamento_confirmar] has_qr_text:", bool(qr.get("qr_code_text")))
        print("[pagamento_confirmar] url:", qr.get("url"))
    request.session[f"qr_{sid}"] = qr
    if ap.payment_status != 'pendente':
        ap.payment_status = 'pendente'
        ap.save(update_fields=["payment_status"])
    return redirect('pagamento', sid=sid)


@require_http_methods(["POST"])
def pagamento_falhar(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    print("[pagamento_falhar] sid:", sid)
    print("[pagamento_falhar] current_status:", ap.payment_status)
    ap.payment_status = 'falhou'
    ap.save(update_fields=["payment_status"])
    print("[pagamento_falhar] new_status:", ap.payment_status)
    return redirect('pagamento', sid=sid)


@require_http_methods(["GET"])
def pagamento_check(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    qr = request.session.get(f"qr_{sid}") or {}
    charge_id = qr.get("charge_id")
    if not charge_id:
        return JsonResponse({"ok": False, "paid": False, "error": "qr_not_found"}, status=400)

    svc = get_abacate_pay_service()
    result = svc.checar_qrcode(charge_id)
    if result.get("ok") and result.get("paid"):
        ap.payment_status = 'pago'
        ap.save(update_fields=["payment_status"])
        try:
            del request.session[f"qr_{sid}"]
        except Exception:
            pass
        return JsonResponse({"ok": True, "paid": True, "status": result.get("status")})
    return JsonResponse({"ok": bool(result.get("ok")), "paid": False, "status": result.get("status"), "error": result.get("error")})


@require_http_methods(["GET"])
def pagamento_sucesso(request, sid):
    ap = get_appointment_by_sid_or_404(sid)
    resp = render(request, 'payments/sucesso.html', {'ap': ap, 'sid': sid})
    resp['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp['Pragma'] = 'no-cache'
    return resp
