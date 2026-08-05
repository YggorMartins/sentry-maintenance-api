"""
Testes unitários dos validadores de CPF/CNPJ.

Usamos CPFs e CNPJs válidos publicamente conhecidos como "números de
teste" (mesma lógica de cartões de teste de gateways de pagamento) —
não pertencem a nenhuma pessoa real, são apenas sequências que passam
no algoritmo de dígito verificador.
"""
from app.utils.document_validators import is_valid_cnpj, is_valid_cpf


def test_cpf_valido_e_aceito():
    assert is_valid_cpf("111.444.777-35") is True


def test_cpf_com_digitos_repetidos_e_rejeitado():
    assert is_valid_cpf("111.111.111-11") is False


def test_cpf_com_digito_verificador_errado_e_rejeitado():
    assert is_valid_cpf("111.444.777-36") is False


def test_cpf_com_tamanho_invalido_e_rejeitado():
    assert is_valid_cpf("123") is False


def test_cnpj_valido_e_aceito():
    assert is_valid_cnpj("11.222.333/0001-81") is True


def test_cnpj_com_digitos_repetidos_e_rejeitado():
    assert is_valid_cnpj("11.111.111/1111-11") is False


def test_cnpj_com_digito_verificador_errado_e_rejeitado():
    assert is_valid_cnpj("11.222.333/0001-82") is False


def test_cnpj_com_tamanho_invalido_e_rejeitado():
    assert is_valid_cnpj("123") is False
