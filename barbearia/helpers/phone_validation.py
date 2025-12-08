from typing import Dict
import re


class PhoneValidator:
    """
    Classe utilitária para validação de números de telefone brasileiros.
    """

    # Conjunto de DDDs válidos no Brasil
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
        """Extrai somente os dígitos do valor informado."""
        raw = ''.join(ch for ch in (value or '') if ch.isdigit())
        if len(raw) >= 3 and raw[2] == '9':
            return raw[:2] + raw[3:]
        return raw

    @staticmethod
    def extract_raw_digits(value: str) -> str:
        return ''.join(ch for ch in (value or '') if ch.isdigit())

    @staticmethod
    def contains_only_numbers(value: str) -> bool:
        """Verifica se a string contém apenas números (sem espaços ou símbolos)."""
        return (value or '').isdigit()

    @classmethod
    def has_correct_length(cls, value: str) -> bool:
        """Confere se o telefone possui 11 dígitos (celular com DDD)."""
        return len(cls.extract_raw_digits(value)) == 11

    @classmethod
    def is_valid_ddd(cls, value: str) -> bool:
        """Valida se o DDD (dois primeiros dígitos) é válido no Brasil."""
        digits = cls.extract_raw_digits(value)
        ddd = digits[:2] if len(digits) >= 2 else ''
        return ddd in cls.VALID_DDD

    @staticmethod
    def matches_br_format(value: str) -> bool:
        """Valida o formato esperado: (DDD) 9XXXX-XXXX (espaço após o 9 é opcional)."""
        return bool(re.fullmatch(r"\(\d{2}\)\s9\s?\d{4}-\d{4}", (value or '')))

    @classmethod
    def is_valid_brazil_number(cls, value: str) -> bool:
        """Valida número de celular brasileiro: 11 dígitos, DDD válido, e começa com 9."""
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
        """Retorna um diagnóstico com o resultado de cada checagem."""
        return {
            'only_numbers': cls.contains_only_numbers(value),
            'correct_length': cls.has_correct_length(value),
            'valid_ddd': cls.is_valid_ddd(value),
            'format_match': cls.matches_br_format(value),
            'valid_brazil_number': cls.is_valid_brazil_number(value),
        }
