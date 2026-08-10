"""
Schemas de Movimentação de Estoque.

`usuario_id` não vem no Create — é preenchido pelo router a partir do
usuário autenticado (não faz sentido confiar no cliente da API pra
dizer "quem" fez a movimentação).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import TipoMovimentacao


class MovimentacaoCreate(BaseModel):
    peca_id: uuid.UUID
    ordem_servico_id: uuid.UUID | None = None
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)
    motivo: str | None = None


class MovimentacaoOut(BaseModel):
    id: uuid.UUID
    peca_id: uuid.UUID
    ordem_servico_id: uuid.UUID | None
    usuario_id: uuid.UUID | None
    tipo: TipoMovimentacao
    quantidade: int
    motivo: str | None
    data: datetime

    model_config = ConfigDict(from_attributes=True)
