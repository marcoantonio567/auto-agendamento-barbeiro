import json
import time
import base64
import hashlib
from typing import Optional, Dict, Any

from django.conf import settings

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:  # pragma: no cover
    Fernet = None
    InvalidToken = Exception


def _get_fernet() -> Fernet:
    """Obtém uma instância `Fernet` baseada em `SELF_SERVICE_TOKEN_KEY` ou `SECRET_KEY`."""
    if Fernet is None:
        raise RuntimeError("cryptography/Fernet não disponível. Instale a dependência.")
    key = getattr(settings, "SELF_SERVICE_TOKEN_KEY", None)
    if not key:
        digest = hashlib.sha256(str(settings.SECRET_KEY).encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(digest)
    elif isinstance(key, str):
        try:
            key = key.encode("utf-8")
            base64.urlsafe_b64decode(key)
        except Exception:
            digest = hashlib.sha256(key).digest()
            key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def gerar_token(payload: Dict[str, Any], ttl_segundos: int = 15 * 60) -> str:
    """Gera token criptografado com campos `iat` e `exp` usando Fernet."""
    agora = int(time.time())
    data = {**payload, "iat": agora, "exp": agora + ttl_segundos}
    texto = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return _get_fernet().encrypt(texto.encode("utf-8")).decode("utf-8")


def validar_token(token: str) -> Optional[Dict[str, Any]]:
    """Valida o token Fernet e retorna o payload se não expirado; caso contrário `None`."""
    try:
        texto = _get_fernet().decrypt(token.encode("utf-8"))
        data = json.loads(texto.decode("utf-8"))
        exp = int(data.get("exp", 0))
        if int(time.time()) > exp:
            return None
        return data
    except (InvalidToken, ValueError, TypeError):
        return None

