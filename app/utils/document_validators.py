"""
Validação de CPF e CNPJ.

Implementa o algoritmo oficial de dígito verificador (não é só checagem
de formato/tamanho) — funções puras, sem dependência de banco ou API,
para serem testadas isoladamente e reaproveitadas nos schemas Pydantic.
"""
import re


def _only_digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def is_valid_cpf(cpf: str) -> bool:
    cpf = _only_digits(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_digit(digits: str, weights: range) -> str:
        total = sum(int(d) * w for d, w in zip(digits, weights))
        remainder = (total * 10) % 11
        return "0" if remainder == 10 else str(remainder)

    d1 = calc_digit(cpf[:9], range(10, 1, -1))
    d2 = calc_digit(cpf[:9] + d1, range(11, 1, -1))
    return cpf[-2:] == d1 + d2


def is_valid_cnpj(cnpj: str) -> bool:
    cnpj = _only_digits(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calc_digit(digits: str, weights: list[int]) -> str:
        total = sum(int(d) * w for d, w in zip(digits, weights))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    d1 = calc_digit(cnpj[:12], weights1)
    d2 = calc_digit(cnpj[:12] + d1, weights2)
    return cnpj[-2:] == d1 + d2
