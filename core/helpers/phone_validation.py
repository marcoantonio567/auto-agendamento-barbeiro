from typing import Dict
import re


class PhoneValidator:
    """
    Classe utilitária para validação de números de telefone brasileiros.
    """

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

    @staticmethod
    def extract_digits(value: str) -> str:
        """Extrai dígitos removendo não-numéricos e descarta '9' logo após o DDD."""
        raw = ''.join(ch for ch in (value or '') if ch.isdigit())
        if len(raw) >= 3 and raw[2] == '9':
            return raw[:2] + raw[3:]
        return raw

    @staticmethod
    def extract_raw_digits(value: str) -> str:
        """Extrai somente os dígitos do valor informado."""
        return ''.join(ch for ch in (value or '') if ch.isdigit())

    @staticmethod
    def contains_only_numbers(value: str) -> bool:
        """Verifica se o valor contém apenas números."""
        return (value or '').isdigit()

    @classmethod
    def has_correct_length(cls, value: str) -> bool:
        """Verifica se há exatamente 11 dígitos após a extração."""
        return len(cls.extract_raw_digits(value)) == 11

    @classmethod
    def is_valid_ddd(cls, value: str) -> bool:
        """Verifica se o DDD extraído está na lista de DDDs válidos."""
        digits = cls.extract_raw_digits(value)
        ddd = digits[:2] if len(digits) >= 2 else ''
        return ddd in cls.VALID_DDD

    @staticmethod
    def matches_br_format(value: str) -> bool:
        """Valida se o formato corresponde a '(DD) 9 9999-9999'."""
        return bool(re.fullmatch(r"\(\d{2}\)\s9\s?\d{4}-\d{4}", (value or '')))

    @classmethod
    def is_valid_brazil_number(cls, value: str) -> bool:
        """Valida número brasileiro com DDD válido e dígito '9' após o DDD."""
        digits = cls.extract_raw_digits(value)
        if len(digits) != 11:
            return False
        if digits[0:2] not in cls.VALID_DDD:
            return False
        if digits[2] != '9':
            return False
        return True

    @classmethod
    def diagnostics(cls, value: str) -> Dict[str, bool]:
        """Retorna um dicionário com diagnósticos de validação do telefone."""
        return {
            'only_numbers': cls.contains_only_numbers(value),
            'correct_length': cls.has_correct_length(value),
            'valid_ddd': cls.is_valid_ddd(value),
            'format_match': cls.matches_br_format(value),
            'valid_brazil_number': cls.is_valid_brazil_number(value),
        }
