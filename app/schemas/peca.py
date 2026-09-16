"""
Schemas de Peça.

`quantidade_atual` aparece só em PecaOut (leitura) — Create/Update não
a expõem, reforçando que ela só muda via movimentação de estoque.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PecaBase(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    descricao: str = Field(min_length=3, max_length=255)
    fornecedor: str | None = Field(default=None, max_length=150)
    valor: float = Field(ge=0)
    localizacao: str | None = Field(default=None, max_length=100)
    lote: str | None = Field(default=None, max_length=50)
    estoque_minimo: int = Field(default=0, ge=0)
    categoria: str = Field(default="componente", min_length=2, max_length=80)


class PecaCreate(PecaBase):
    pass


class PecaUpdate(PecaBase):
    pass


class PecaOut(PecaBase):
    id: uuid.UUID
    quantidade_atual: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
