"""Router de Ordem de Serviço — endpoints REST + endpoint dedicado de status."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.enums import StatusOS
from app.core.exceptions import (
    AeronaveNotFoundError,
    MotorNotFoundError,
    OrdemServicoNaoEditavelError,
    OrdemServicoNotFoundError,
    ResponsavelInvalidoError,
    TransicaoStatusInvalidaError,
)
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.common import PaginatedResponse
from app.schemas.ordem_servico import (
    OrdemServicoCreate,
    OrdemServicoOut,
    OrdemServicoStatusUpdate,
    OrdemServicoUpdate,
)
from app.services.ordem_servico_service import OrdemServicoService

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])

pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_gerenciar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR])
pode_excluir = RoleChecker([UserRole.ADMIN])


def _tratar_erros_de_negocio(exc: Exception):
    if isinstance(exc, OrdemServicoNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada.")
    if isinstance(exc, AeronaveNotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aeronave informada não existe.")
    if isinstance(exc, MotorNotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Motor informado não existe.")
    if isinstance(exc, ResponsavelInvalidoError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mecânico/inspetor informado não existe ou não possui o papel correto.",
        )
    if isinstance(exc, TransicaoStatusInvalidaError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transição de status não permitida a partir do status atual.",
        )
    if isinstance(exc, OrdemServicoNaoEditavelError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ordem de serviço não pode ser editada/excluída neste status.",
        )
    raise exc


@router.post("", response_model=OrdemServicoOut, status_code=status.HTTP_201_CREATED)
def create_ordem_servico(
    data: OrdemServicoCreate, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)
):
    try:
        return OrdemServicoService(db).create(data)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.get("", response_model=PaginatedResponse[OrdemServicoOut])
def list_ordens_servico(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    aeronave_id: uuid.UUID | None = Query(default=None),
    status_filtro: StatusOS | None = Query(default=None, alias="status"),
    mecanico_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    items, total = OrdemServicoService(db).list(
        page=page,
        page_size=page_size,
        aeronave_id=aeronave_id,
        status_filtro=status_filtro,
        mecanico_id=mecanico_id,
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{os_id}", response_model=OrdemServicoOut)
def get_ordem_servico(os_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_consultar)):
    try:
        return OrdemServicoService(db).get(os_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.put("/{os_id}", response_model=OrdemServicoOut)
def update_ordem_servico(
    os_id: uuid.UUID,
    data: OrdemServicoUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        return OrdemServicoService(db).update(os_id, data)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.patch("/{os_id}/status", response_model=OrdemServicoOut)
def update_status_ordem_servico(
    os_id: uuid.UUID,
    data: OrdemServicoStatusUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        return OrdemServicoService(db).update_status(os_id, data.status)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.delete("/{os_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ordem_servico(os_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_excluir)):
    try:
        OrdemServicoService(db).delete(os_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)
