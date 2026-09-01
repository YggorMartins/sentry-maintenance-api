"""
Service de Anexo.

Como `entidade_tipo`/`entidade_id` não têm FOREIGN KEY nativa (ver
explicação no model), este service é responsável por validar "na mão"
que a entidade referenciada realmente existe, despachando para o
repository certo conforme o tipo.
"""
import io
import re
import unicodedata
import uuid
import zipfile
from pathlib import Path

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

EXTENSOES_POR_CONTENT_TYPE = {
    "application/pdf": {".pdf"},
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "application/msword": {".doc"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {".docx"},
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
        nome = re.sub(r"[^A-Za-z0-9._-]", "_", Path(nome).name)
        return nome if nome not in {"", ".", ".."} else "arquivo"

    @staticmethod
    def detectar_content_type(conteudo: bytes) -> str | None:
        """Detecta formatos permitidos pela assinatura, sem confiar no header HTTP."""
        if conteudo.startswith(b"%PDF-"):
            return "application/pdf"
        if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if conteudo.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if conteudo.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            return "application/msword"
        if conteudo.startswith(b"PK\x03\x04"):
            try:
                with zipfile.ZipFile(io.BytesIO(conteudo)) as archive:
                    names = set(archive.namelist())
            except (OSError, zipfile.BadZipFile):
                return None
            if "[Content_Types].xml" in names and any(
                name.startswith("word/") for name in names
            ):
                return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return None

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

        tamanho_maximo = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if not conteudo or len(conteudo) > tamanho_maximo:
            raise ArquivoInvalidoError()

        content_type_detectado = self.detectar_content_type(conteudo)
        if content_type_detectado not in CONTENT_TYPES_PERMITIDOS:
            raise ArquivoInvalidoError()
        if content_type not in {content_type_detectado, "application/octet-stream"}:
            raise ArquivoInvalidoError()

        subdir = f"{entidade_tipo.value}/{entidade_id}"
        nome_seguro = self._sanitizar_nome_arquivo(nome_original)
        if Path(nome_seguro).suffix.lower() not in EXTENSOES_POR_CONTENT_TYPE[content_type_detectado]:
            raise ArquivoInvalidoError()
        caminho_relativo = self.storage.save(conteudo, subdir, nome_seguro)

        anexo = Anexo(
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            nome_original=nome_seguro,
            caminho_arquivo=caminho_relativo,
            content_type=content_type_detectado,
            tamanho_bytes=len(conteudo),
            descricao=descricao,
            usuario_id=usuario_id,
        )
        try:
            return self.repository.create(anexo)
        except Exception:
            self.storage.delete(caminho_relativo)
            raise

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
