import logging
import re
from decouple import config
import requests
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def _normalize_number(number: str, default_country_code: str = "55") -> str:
    digits = re.sub(r"\D+", "", number or "")
    if not digits:
        return ""
    if digits.startswith(default_country_code):
        return digits
    return f"{default_country_code}{digits}"

def send_mensage(number: str, text: str) -> Dict[str, Any]:
    base_url = config("EVOLUTION_API_URL", default="http://localhost:8082")
    api_key = config("EVOLUTION_API_KEY", default="")
    url = base_url.rstrip("/") + "/message/sendText/main_phone"
    normalized_number = _normalize_number(number)
    if not normalized_number or len(normalized_number) < 12:
        return {
            "ok": False,
            "status_code": None,
            "error": "invalid_number",
            "details": "Número inválido ou ausente"
        }
    if not api_key:
        return {
            "ok": False,
            "status_code": None,
            "error": "missing_api_key",
            "details": "EVOLUTION_API_KEY não configurada"
        }
    payload = {
        "number": normalized_number,
        "textMessage": {
            "text": text
        },
    }
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}
        logger.info("Mensagem enviada para %s", normalized_number)
        return {
            "ok": True,
            "status_code": response.status_code,
            "data": data
        }
    except requests.exceptions.Timeout:
        logger.warning("Timeout ao enviar mensagem para %s", normalized_number)
        return {
            "ok": False,
            "status_code": None,
            "error": "timeout",
            "details": "Tempo de requisição excedido"
        }
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        body = None
        try:
            body = e.response.json() if e.response is not None else None
        except ValueError:
            body = e.response.text if e.response is not None else None
        logger.error("HTTP %s ao enviar mensagem para %s", status, normalized_number)
        return {
            "ok": False,
            "status_code": status,
            "error": "http_error",
            "details": body
        }
    except requests.exceptions.ConnectionError:
        logger.error("Conexão falhou ao enviar mensagem para %s", normalized_number)
        return {
            "ok": False,
            "status_code": None,
            "error": "connection_error",
            "details": "Falha de conexão com Evolution API"
        }
    except Exception as e:
        logger.exception("Erro inesperado ao enviar mensagem para %s", normalized_number)
        return {
            "ok": False,
            "status_code": None,
            "error": "unexpected_error",
            "details": str(e)
        }
