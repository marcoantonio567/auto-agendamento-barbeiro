from datetime import date as ddate, timedelta
from .slots import slots_for_day
from django.shortcuts import redirect



def dia_e_hora_validos(day, hr):
    """Valida se o dia está nos próximos 7 dias e a hora é um slot válido."""
    today = ddate.today()
    if day < today or day > today + timedelta(days=7):
        return False
    return hr in slots_for_day(day)

def verificar_step(request, step):
    """Verifica se o passo existe na sessão; redireciona se ausente."""
    if not request.session.get(step):
        return redirect(f'step_{step}')


def get_hours_delta_from_direction(direction):
    """Retorna delta de horas com base na direção ('prev'=-1, 'next'=1)."""
    if direction == 'prev':
        return -1
    if direction == 'next':
        return 1
    return None


VALID_DDD = {
    '11','12','13','14','15','16','17','18','19',
    '21','22','24','27','28',
    '31','32','33','34','35','37','38',
    '41','42','43','44','45','46',
    '47','48','49',
    '51','53','54','55',
    '61','62','63','64','65','66','67','68','69',
    '71','73','74','75','77','79',
    '81','82','83','84','85','86','87','88','89',
    '91','92','93','94','95','96','97','98','99'
}


def extrair_digitos(s):
    """Extrai apenas os dígitos de `s`."""
    return ''.join(ch for ch in (s or '') if ch.isdigit())


def telefone_contem_apenas_numeros(s):
    """Retorna True se `s` contém somente números."""
    return (s or '').isdigit()


def telefone_tem_comprimento_correto(s):
    """Retorna True se `s` possui exatamente 11 dígitos."""
    return len(extrair_digitos(s)) == 11


def validar_ddd(s):
    """Valida se o DDD está na lista de DDDs permitidos."""
    d = extrair_digitos(s)
    ddd = d[:2] if len(d) >= 2 else ''
    return ddd in VALID_DDD


def validar_formato_telefone(s):
    """Valida se o formato corresponde a '(DD) 9 9999-9999'."""
    import re
    return bool(re.fullmatch(r"\(\d{2}\)\s9\s?\d{4}-\d{4}", (s or '')))


def validar_telefone_brasil(s):
    """Valida número com DDD válido, dígito 9 após o DDD e 11 dígitos."""
    d = extrair_digitos(s)
    if len(d) != 11:
        return False
    if d[0:2] not in VALID_DDD:
        return False
    if d[2] != '9':
        return False
    return True
