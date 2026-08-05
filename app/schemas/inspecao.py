"""Schemas de Inspeção."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import TipoInspecao


class InspecaoBase(BaseModel):
    ordem_servico_id: uuid.UUID
    responsavel_id: uuid.UUID
    tipo: TipoInspecao
    data: date
    horas_aeronave: int = Field(ge=0)
    itens_executados: str = Field(min_length=3)
    pendencias: str | None = None
    proxima_inspecao: date | None = None

    @model_validator(mode="after")
    def validar_proxima_inspecao_apos_data(self) -> "InspecaoBase":
        if self.proxima_inspecao is not None and self.proxima_inspecao <= self.data:
            raise ValueError("A próxima inspeção deve ser posterior à data desta inspeção.")
        return self


class InspecaoCreate(InspecaoBase):
    pass


class InspecaoUpdate(InspecaoBase):
    pass


class InspecaoOut(InspecaoBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
