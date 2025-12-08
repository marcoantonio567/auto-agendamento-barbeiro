import json
import requests
from decouple import config


class AbacatePayService:
    def __init__(self):
        self.base_url = "https://api.abacatepay.com/v1"
        self.api_key = config("ABACATEPAY_KEY", default="")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        print("[AbacatePayService.__init__] headers:", self.headers)
        print("[AbacatePayService.__init__] api_key_configured:", bool(self.api_key))

    def gerar_qrcode(self, amount: float, description: str = "", metadata: dict | None = None) -> dict:
        if not self.api_key:
            return {"ok": False, "error": "Chave ABACATEPAY_KEY não configurada"}
        amount_cents = int(amount * 100)

        payload = {
            "amount": amount_cents,
            "description": description or "Pagamento",
            "metadata": metadata or {},
        }
        print("[AbacatePayService.gerar_qrcode] url:", f"{self.base_url}/pixQrCode/create")
        print("[AbacatePayService.gerar_qrcode] payload:", payload)

        try:
            resp = requests.post(
                f"{self.base_url}/pixQrCode/create",
                headers=self.headers,
                json=payload,
                timeout=15,
            )

            wrapper = resp.json()
            print("[AbacatePayService.gerar_qrcode] status_code:", resp.status_code)
            print("[AbacatePayService.gerar_qrcode] response_keys:", list(wrapper.keys()))

            if isinstance(wrapper, dict) and wrapper.get("error"):
                return {"ok": False, "error": wrapper.get("error")}

            data = wrapper.get("data") if isinstance(wrapper, dict) else None
            if data is None:
                data = wrapper

            if not resp.ok and not data:
                return {"ok": False, "error": wrapper}

            b64_or_url = (data or {}).get("brCodeBase64")
            qr_code_image_url = None
            base64_img = None
            if b64_or_url:
                if str(b64_or_url).startswith("data:image"):
                    qr_code_image_url = b64_or_url
                    try:
                        base64_img = b64_or_url.split(",", 1)[1]
                    except Exception:
                        base64_img = None
                else:
                    base64_img = b64_or_url
                    qr_code_image_url = f"data:image/png;base64,{base64_img}"

            print("[AbacatePayService.gerar_qrcode] status:", (data or {}).get("status"))
            print("[AbacatePayService.gerar_qrcode] devMode:", (data or {}).get("devMode"))
            print("[AbacatePayService.gerar_qrcode] method:", (data or {}).get("method"))
            print("[AbacatePayService.gerar_qrcode] id:", (data or {}).get("id"))

            return {
                "ok": True,
                "charge_id": (data or {}).get("id"),
                "qr_code_text": (data or {}).get("brCode"),
                "qr_code_image_base64": base64_img,
                "qr_code_image_url": qr_code_image_url,
                "url": (data or {}).get("url"),
                "status": (data or {}).get("status"),
                "method": (data or {}).get("method"),
                "dev_mode": (data or {}).get("devMode"),
                "amount_cents": (data or {}).get("amount"),
                "amount": ((data or {}).get("amount") / 100) if isinstance((data or {}).get("amount"), (int, float)) else None,
                "created_at": (data or {}).get("createdAt"),
                "expires_at": (data or {}).get("expiresAt"),
            }

        except Exception as e:
            print("[AbacatePayService.gerar_qrcode] exception:", e)
            return {"ok": False, "error": str(e)}

    def checar_qrcode(self, charge_id: str) -> dict:
        if not self.api_key:
            return {"ok": False, "error": "Chave ABACATEPAY_KEY não configurada"}
        if not charge_id:
            return {"ok": False, "error": "ID do QRCode ausente"}

        url = f"{self.base_url}/pixQrCode/check"
        print("[AbacatePayService.checar_qrcode] url:", url, "id:", charge_id)
        try:
            resp = requests.get(url, headers=self.headers, params={"id": charge_id}, timeout=10)
            wrapper = resp.json()
            print("[AbacatePayService.checar_qrcode] status_code:", resp.status_code)
            print("[AbacatePayService.checar_qrcode] response_keys:", list(wrapper.keys()) if isinstance(wrapper, dict) else type(wrapper))

            if isinstance(wrapper, dict) and wrapper.get("error"):
                return {"ok": False, "error": wrapper.get("error")}

            data = wrapper.get("data") if isinstance(wrapper, dict) else None
            if data is None:
                data = wrapper

            status = str((data or {}).get("status") or "").lower()
            paid_flag = (data or {}).get("paid")
            paid = bool(paid_flag) or status in {"paid", "pago", "confirmed", "confirmado", "approved"}

            return {
                "ok": True,
                "paid": paid,
                "status": (data or {}).get("status"),
                "data": data,
            }
        except Exception as e:
            print("[AbacatePayService.checar_qrcode] exception:", e)
            return {"ok": False, "error": str(e)}


def get_abacate_pay_service() -> "AbacatePayService":
    return AbacatePayService()
