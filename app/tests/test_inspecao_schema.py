"""Teste unitário da validação de datas do schema de Inspeção (sem banco)."""
import uuid
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.inspecao import InspecaoCreate


def _inspecao_valida(**overrides) -> dict:
    base = dict(
        ordem_servico_id=uuid.uuid4(),
        responsavel_id=uuid.uuid4(),
        tipo="anual",
        data=date(2026, 1, 10),
        horas_aeronave=1200,
        itens_executados="Troca de filtro de óleo, inspeção visual da fuselagem.",
    )
    base.update(overrides)
    return base


def test_proxima_inspecao_posterior_a_data_e_valida():
    inspecao = InspecaoCreate(**_inspecao_valida(proxima_inspecao=date(2027, 1, 10)))
    assert inspecao.proxima_inspecao > inspecao.data


def test_proxima_inspecao_anterior_a_data_e_rejeitada():
    with pytest.raises(ValidationError):
        InspecaoCreate(**_inspecao_valida(proxima_inspecao=date(2025, 1, 1)))


def test_proxima_inspecao_igual_a_data_e_rejeitada():
    with pytest.raises(ValidationError):
        InspecaoCreate(**_inspecao_valida(proxima_inspecao=date(2026, 1, 10)))


def test_proxima_inspecao_ausente_e_valida():
    inspecao = InspecaoCreate(**_inspecao_valida())
    assert inspecao.proxima_inspecao is None
