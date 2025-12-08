from datetime import date as ddate, timedelta
from .slots import slots_for_day
from django.shortcuts import redirect



def dia_e_hora_validos(day, hr):
    """Confere se o dia está dentro dos próximos 7 dias e se a hora é válida."""
    today = ddate.today()
    if day < today or day > today + timedelta(days=7):
        return False
    return hr in slots_for_day(day)

def verificar_step(request, step):
    """
    Verifica se o usuário passou na etapa do anterior.
    Se não estiver, redireciona para a etapa do anterior.
    """
    if not request.session.get(step):
        return redirect(f'step_{step}')


def get_hours_delta_from_direction(direction):
    """Retorna o delta de horas a partir da direção.

    - direction: 'prev' -> -1 hora, 'next' -> +1 hora
    - retorna None se a direção for inválida
    """
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
    return ''.join(ch for ch in (s or '') if ch.isdigit())


def telefone_contem_apenas_numeros(s):
    return (s or '').isdigit()


def telefone_tem_comprimento_correto(s):
    return len(extrair_digitos(s)) == 11


def validar_ddd(s):
    d = extrair_digitos(s)
    ddd = d[:2] if len(d) >= 2 else ''
    return ddd in VALID_DDD


def validar_formato_telefone(s):
    import re
    return bool(re.fullmatch(r"\(\d{2}\)\s9\s?\d{4}-\d{4}", (s or '')))


def validar_telefone_brasil(s):
    d = extrair_digitos(s)
    if len(d) != 11:
        return False
    if d[0:2] not in VALID_DDD:
        return False
    if d[2] != '9':
        return False
    return True
