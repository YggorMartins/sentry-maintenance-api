"""Router de Anexo — upload multipart/form-data, listagem, metadados e download."""
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.enums import TipoEntidadeAnexo
from app.core.exceptions import (
    AnexoNotFoundError,
    ArquivoInvalidoError,
    EntidadeReferenciadaNotFoundError,
)
from app.core.roles import UserRole
from app.core.storage import StorageBackend, get_storage_backend
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.models.user import User
from app.schemas.anexo import AnexoOut
from app.schemas.common import PaginatedResponse
from app.services.anexo_service import AnexoService

router = APIRouter(prefix="/anexos", tags=["Anexos"])

pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_enviar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_excluir = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR])


async def _read_limited_upload(file: UploadFile) -> bytes:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = bytearray()
    try:
        while chunk := await file.read(64 * 1024):
            if len(content) + len(chunk) > max_bytes:
                raise ArquivoInvalidoError()
            content.extend(chunk)
    finally:
        await file.close()
    return bytes(content)


def _tratar_erros_de_negocio(exc: Exception):
    if isinstance(exc, AnexoNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anexo não encontrado.")
    if isinstance(exc, EntidadeReferenciadaNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A entidade referenciada (aeronave/OS/cliente/inspeção) não existe.",
        )
    if isinstance(exc, ArquivoInvalidoError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tipo de arquivo não suportado ou tamanho acima do limite permitido.",
        )
    raise exc


@router.post("", response_model=AnexoOut, status_code=status.HTTP_201_CREATED)
async def upload_anexo(
    entidade_tipo: TipoEntidadeAnexo = Form(...),
    entidade_id: uuid.UUID = Form(...),
    descricao: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage: StorageBackend = Depends(get_storage_backend),
    current_user: User = Depends(pode_enviar),
):
    try:
        conteudo = await _read_limited_upload(file)
        return AnexoService(db, storage).upload(
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            nome_original=file.filename or "arquivo",
            content_type=file.content_type or "application/octet-stream",
            conteudo=conteudo,
            descricao=descricao,
            usuario_id=current_user.id,
        )
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.get("", response_model=PaginatedResponse[AnexoOut])
def list_anexos(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    entidade_tipo: TipoEntidadeAnexo | None = Query(default=None),
    entidade_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    storage: StorageBackend = Depends(get_storage_backend),
    _: object = Depends(pode_consultar),
):
    items, total = AnexoService(db, storage).list(
        page=page, page_size=page_size, entidade_tipo=entidade_tipo, entidade_id=entidade_id
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{anexo_id}", response_model=AnexoOut)
def get_anexo(
    anexo_id: uuid.UUID,
    db: Session = Depends(get_db),
    storage: StorageBackend = Depends(get_storage_backend),
    _: object = Depends(pode_consultar),
):
    try:
        return AnexoService(db, storage).get(anexo_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.get("/{anexo_id}/download")
def download_anexo(
    anexo_id: uuid.UUID,
    db: Session = Depends(get_db),
    storage: StorageBackend = Depends(get_storage_backend),
    _: object = Depends(pode_consultar),
):
    try:
        anexo = AnexoService(db, storage).get(anexo_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)
        return

    caminho_absoluto = storage.get_full_path(anexo.caminho_arquivo)
    if not caminho_absoluto.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado em disco.")

    return FileResponse(
        path=caminho_absoluto,
        media_type=anexo.content_type,
        filename=anexo.nome_original,
    )


@router.delete("/{anexo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anexo(
    anexo_id: uuid.UUID,
    db: Session = Depends(get_db),
    storage: StorageBackend = Depends(get_storage_backend),
    _: object = Depends(pode_excluir),
):
    try:
        AnexoService(db, storage).delete(anexo_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)
