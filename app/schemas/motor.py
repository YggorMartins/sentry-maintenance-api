"""Schemas de Motor."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MotorBase(BaseModel):
    fabricante: str = Field(min_length=2, max_length=100)
    modelo: str = Field(min_length=1, max_length=100)
    numero_serie: str = Field(min_length=1, max_length=50)
    tsn: int = Field(default=0, ge=0)
    tso: int = Field(default=0, ge=0)
    tbo: int = Field(gt=0)
    ultima_inspecao: date | None = None

    @model_validator(mode="after")
    def validar_tso_nao_maior_que_tsn(self) -> "MotorBase":
        if self.tso > self.tsn:
            raise ValueError("TSO (horas desde overhaul) não pode ser maior que TSN (horas desde novo).")
        return self


class MotorCreate(MotorBase):
    pass


class MotorUpdate(MotorBase):
    pass


class MotorOut(MotorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
