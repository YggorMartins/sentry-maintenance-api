import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import RecorrenciaManutencao, StatusAgendamento, TipoManutencao


class AgendamentoCreate(BaseModel):
    aeronave_id: uuid.UUID
    tecnico_id: uuid.UUID | None = None
    titulo: str = Field(min_length=3, max_length=160)
    descricao: str | None = Field(default=None, max_length=2000)
    inicio: datetime
    fim: datetime
    tipo: TipoManutencao
    recorrencia: RecorrenciaManutencao = RecorrenciaManutencao.NENHUMA
    recorrencia_ate: datetime | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.fim <= self.inicio:
            raise ValueError("fim deve ser posterior ao início")
        if self.recorrencia_ate and self.recorrencia_ate < self.inicio:
            raise ValueError("recorrencia_ate não pode ser anterior ao início")
        return self


class AgendamentoUpdate(BaseModel):
    tecnico_id: uuid.UUID | None = None
    titulo: str = Field(min_length=3, max_length=160)
    descricao: str | None = Field(default=None, max_length=2000)
    inicio: datetime
    fim: datetime
    tipo: TipoManutencao
    recorrencia: RecorrenciaManutencao = RecorrenciaManutencao.NENHUMA
    recorrencia_ate: datetime | None = None
    status: StatusAgendamento

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.fim <= self.inicio:
            raise ValueError("fim deve ser posterior ao início")
        return self


class AgendamentoOut(BaseModel):
    id: uuid.UUID
    aeronave_id: uuid.UUID
    tecnico_id: uuid.UUID | None
    titulo: str
    descricao: str | None
    inicio: datetime
    fim: datetime
    tipo: TipoManutencao
    recorrencia: RecorrenciaManutencao
    recorrencia_ate: datetime | None
    status: StatusAgendamento
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
