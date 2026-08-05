"""
Schemas de Ordem de Serviço.

Note que `numero`, `status`, `data_abertura` e `data_fechamento` NÃO
aparecem em OrdemServicoCreate/Update — são controlados pelo sistema
(numero e data_abertura na criação; status e data_fechamento só pelo
endpoint dedicado de transição). Isso evita que o cliente da API force
um estado inconsistente.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import StatusOS


class OrdemServicoCreate(BaseModel):
    aeronave_id: uuid.UUID
    motor_id: uuid.UUID | None = None
    mecanico_id: uuid.UUID | None = None
    inspetor_id: uuid.UUID | None = None
    descricao: str = Field(min_length=5)
    observacoes: str | None = None


class OrdemServicoUpdate(BaseModel):
    motor_id: uuid.UUID | None = None
    mecanico_id: uuid.UUID | None = None
    inspetor_id: uuid.UUID | None = None
    descricao: str = Field(min_length=5)
    horas_trabalhadas: float = Field(default=0, ge=0)
    observacoes: str | None = None


class OrdemServicoStatusUpdate(BaseModel):
    status: StatusOS


class OrdemServicoOut(BaseModel):
    id: uuid.UUID
    numero: str
    aeronave_id: uuid.UUID
    motor_id: uuid.UUID | None
    mecanico_id: uuid.UUID | None
    inspetor_id: uuid.UUID | None
    descricao: str
    status: StatusOS
    data_abertura: datetime
    data_fechamento: datetime | None
    horas_trabalhadas: float
    observacoes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
