"""Schemas de Aeronave."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import CategoriaAeronave, StatusAeronave
from app.schemas.motor import MotorOut


class AeronaveBase(BaseModel):
    prefixo: str = Field(min_length=3, max_length=10)
    fabricante: str = Field(min_length=2, max_length=100)
    modelo: str = Field(min_length=1, max_length=100)
    numero_serie: str = Field(min_length=1, max_length=50)
    ano: int = Field(ge=1900, le=2100)
    categoria: CategoriaAeronave
    horas_totais: int = Field(default=0, ge=0)
    status: StatusAeronave = StatusAeronave.ATIVA
    motor_id: uuid.UUID | None = None
    cliente_id: uuid.UUID


class AeronaveCreate(AeronaveBase):
    pass


class AeronaveUpdate(AeronaveBase):
    pass


class AeronaveOut(AeronaveBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    motor: MotorOut | None = None

    model_config = ConfigDict(from_attributes=True)
