"""
Teste unitário do schema de Motor.

`tso <= tsn` é uma invariante de domínio (não faz sentido um motor ter
mais horas desde o overhaul do que desde que era novo) validada no
Pydantic — não depende de banco, então cabe aqui junto dos outros
testes unitários puros.
"""
import pytest
from pydantic import ValidationError

from app.schemas.motor import MotorCreate


def _motor_valido(**overrides) -> dict:
    base = dict(
        fabricante="Lycoming",
        modelo="O-360",
        numero_serie="L-12345-51A",
        tsn=500,
        tso=100,
        tbo=2000,
    )
    base.update(overrides)
    return base


def test_motor_com_tso_menor_que_tsn_e_valido():
    motor = MotorCreate(**_motor_valido())
    assert motor.tso <= motor.tsn


def test_motor_com_tso_maior_que_tsn_e_rejeitado():
    with pytest.raises(ValidationError):
        MotorCreate(**_motor_valido(tsn=100, tso=500))


def test_motor_com_tbo_zero_e_rejeitado():
    with pytest.raises(ValidationError):
        MotorCreate(**_motor_valido(tbo=0))
