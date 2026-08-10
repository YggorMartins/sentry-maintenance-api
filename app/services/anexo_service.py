"""
Service de Anexo.

Como `entidade_tipo`/`entidade_id` não têm FOREIGN KEY nativa (ver
explicação no model), este service é responsável por validar "na mão"
que a entidade referenciada realmente existe, despachando para o
repository certo conforme o tipo.
"""
import re
import unicodedata
import uuid

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.enums import TipoEntidadeAnexo
from app.core.exceptions import (
    AnexoNotFoundError,
    ArquivoInvalidoError,
    EntidadeReferenciadaNotFoundError,
)
from app.core.storage import StorageBackend
from app.models.anexo import Anexo
from app.repositories.aeronave_repository import AeronaveRepository
from app.repositories.anexo_repository import AnexoRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.inspecao_repository import InspecaoRepository
from app.repositories.ordem_servico_repository import OrdemServicoRepository

CONTENT_TYPES_PERMITIDOS = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class AnexoService:
    def __init__(self, db: Session, storage: StorageBackend):
        self.repository = AnexoRepository(db)
        self.storage = storage
        # Mapa tipo -> repository, usado para validar existência da
        # entidade referenciada de forma genérica (sem um if/elif gigante
        # espalhado pelo service).
        self._repositorios_por_tipo = {
            TipoEntidadeAnexo.AERONAVE: AeronaveRepository(db),
            TipoEntidadeAnexo.ORDEM_SERVICO: OrdemServicoRepository(db),
            TipoEntidadeAnexo.CLIENTE: ClienteRepository(db),
            TipoEntidadeAnexo.INSPECAO: InspecaoRepository(db),
        }

    def _validar_entidade_existe(self, entidade_tipo: TipoEntidadeAnexo, entidade_id: uuid.UUID) -> None:
        repo = self._repositorios_por_tipo[entidade_tipo]
        if repo.get_by_id(entidade_id) is None:
            raise EntidadeReferenciadaNotFoundError()

    @staticmethod
    def _sanitizar_nome_arquivo(nome: str) -> str:
        nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^A-Za-z0-9._-]", "_", nome)

    def upload(
        self,
        entidade_tipo: TipoEntidadeAnexo,
        entidade_id: uuid.UUID,
        nome_original: str,
        content_type: str,
        conteudo: bytes,
        descricao: str | None,
        usuario_id: uuid.UUID | None,
    ) -> Anexo:
        self._validar_entidade_existe(entidade_tipo, entidade_id)

        if content_type not in CONTENT_TYPES_PERMITIDOS:
            raise ArquivoInvalidoError()

        tamanho_maximo = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(conteudo) > tamanho_maximo:
            raise ArquivoInvalidoError()

        subdir = f"{entidade_tipo.value}/{entidade_id}"
        nome_seguro = self._sanitizar_nome_arquivo(nome_original)
        caminho_relativo = self.storage.save(conteudo, subdir, nome_seguro)

        anexo = Anexo(
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            nome_original=nome_original,
            caminho_arquivo=caminho_relativo,
            content_type=content_type,
            tamanho_bytes=len(conteudo),
            descricao=descricao,
            usuario_id=usuario_id,
        )
        return self.repository.create(anexo)

    def get(self, anexo_id: uuid.UUID) -> Anexo:
        anexo = self.repository.get_by_id(anexo_id)
        if anexo is None:
            raise AnexoNotFoundError()
        return anexo

    def list(
        self,
        page: int,
        page_size: int,
        entidade_tipo: TipoEntidadeAnexo | None = None,
        entidade_id: uuid.UUID | None = None,
    ) -> tuple[list[Anexo], int]:
        return self.repository.list(page=page, page_size=page_size, entidade_tipo=entidade_tipo, entidade_id=entidade_id)

    def delete(self, anexo_id: uuid.UUID) -> None:
        anexo = self.get(anexo_id)
        self.storage.delete(anexo.caminho_arquivo)
        self.repository.delete(anexo)
