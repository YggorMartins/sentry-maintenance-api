"""
Schema de Anexo.

Não existe AnexoCreate como schema JSON — o upload é multipart/form-data
(arquivo binário + campos de formulário), então o router recebe os
campos via `Form(...)` e `File(...)` diretamente, não via um BaseModel
de corpo JSON. Ver app/routers/anexo.py.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import TipoEntidadeAnexo


class AnexoOut(BaseModel):
    id: uuid.UUID
    entidade_tipo: TipoEntidadeAnexo
    entidade_id: uuid.UUID
    nome_original: str
    content_type: str
    tamanho_bytes: int
    descricao: str | None
    usuario_id: uuid.UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
