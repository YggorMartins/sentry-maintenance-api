"""Teste unitário do schema de Movimentação de Estoque (sem banco)."""
import uuid

import pytest
from pydantic import ValidationError

from app.schemas.movimentacao import MovimentacaoCreate


def test_quantidade_positiva_e_valida():
    mov = MovimentacaoCreate(peca_id=uuid.uuid4(), tipo="entrada", quantidade=10)
    assert mov.quantidade == 10


def test_quantidade_zero_e_rejeitada():
    with pytest.raises(ValidationError):
        MovimentacaoCreate(peca_id=uuid.uuid4(), tipo="entrada", quantidade=0)


def test_quantidade_negativa_e_rejeitada():
    with pytest.raises(ValidationError):
        MovimentacaoCreate(peca_id=uuid.uuid4(), tipo="saida", quantidade=-5)
