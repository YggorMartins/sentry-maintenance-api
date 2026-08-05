"""
Service de Aeronave.

Regras de negócio validadas ANTES de tocar o banco:
- prefixo e número de série únicos
- proprietário (cliente_id) precisa existir
- se motor_id for informado, o motor precisa existir e não pode já
  estar instalado em outra aeronave
"""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AeronaveAlreadyExistsError,
    AeronaveNotFoundError,
    MotorJaInstaladoError,
    MotorNotFoundError,
    ProprietarioNotFoundError,
)
from app.models.aeronave import Aeronave
from app.repositories.aeronave_repository import AeronaveRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.motor_repository import MotorRepository
from app.schemas.aeronave import AeronaveCreate, AeronaveUpdate


class AeronaveService:
    def __init__(self, db: Session):
        self.repository = AeronaveRepository(db)
        self.clientes = ClienteRepository(db)
        self.motores = MotorRepository(db)

    def _validar_dados(self, data: AeronaveCreate | AeronaveUpdate, ignorar_id: uuid.UUID | None = None) -> None:
        existente_prefixo = self.repository.get_by_prefixo(data.prefixo)
        if existente_prefixo is not None and existente_prefixo.id != ignorar_id:
            raise AeronaveAlreadyExistsError()

        existente_serie = self.repository.get_by_numero_serie(data.numero_serie)
        if existente_serie is not None and existente_serie.id != ignorar_id:
            raise AeronaveAlreadyExistsError()

        if self.clientes.get_by_id(data.cliente_id) is None:
            raise ProprietarioNotFoundError()

        if data.motor_id is not None:
            if self.motores.get_by_id(data.motor_id) is None:
                raise MotorNotFoundError()
            aeronave_com_motor = self.repository.get_by_motor_id(data.motor_id)
            if aeronave_com_motor is not None and aeronave_com_motor.id != ignorar_id:
                raise MotorJaInstaladoError()

    def create(self, data: AeronaveCreate) -> Aeronave:
        self._validar_dados(data)
        return self.repository.create(data)

    def get(self, aeronave_id: uuid.UUID) -> Aeronave:
        aeronave = self.repository.get_by_id(aeronave_id)
        if aeronave is None:
            raise AeronaveNotFoundError()
        return aeronave

    def list(self, page: int, page_size: int, cliente_id: uuid.UUID | None = None) -> tuple[list[Aeronave], int]:
        return self.repository.list(page=page, page_size=page_size, cliente_id=cliente_id)

    def update(self, aeronave_id: uuid.UUID, data: AeronaveUpdate) -> Aeronave:
        aeronave = self.get(aeronave_id)
        self._validar_dados(data, ignorar_id=aeronave_id)
        return self.repository.update(aeronave, data)

    def delete(self, aeronave_id: uuid.UUID) -> None:
        aeronave = self.get(aeronave_id)
        self.repository.delete(aeronave)
