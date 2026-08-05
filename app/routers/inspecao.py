"""Router de Inspeção — endpoints REST."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.enums import TipoInspecao
from app.core.exceptions import (
    InspecaoNotFoundError,
    OrdemServicoNotFoundError,
    ResponsavelInvalidoError,
)
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.common import PaginatedResponse
from app.schemas.inspecao import InspecaoCreate, InspecaoOut, InspecaoUpdate
from app.services.inspecao_service import InspecaoService

router = APIRouter(prefix="/inspecoes", tags=["Inspeções"])

pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_gerenciar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_excluir = RoleChecker([UserRole.ADMIN])


def _tratar_erros_de_negocio(exc: Exception):
    if isinstance(exc, InspecaoNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspeção não encontrada.")
    if isinstance(exc, OrdemServicoNotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ordem de serviço informada não existe.")
    if isinstance(exc, ResponsavelInvalidoError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Responsável informado não existe ou não é um inspetor.",
        )
    raise exc


@router.post("", response_model=InspecaoOut, status_code=status.HTTP_201_CREATED)
def create_inspecao(data: InspecaoCreate, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)):
    try:
        return InspecaoService(db).create(data)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.get("", response_model=PaginatedResponse[InspecaoOut])
def list_inspecoes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    aeronave_id: uuid.UUID | None = Query(default=None),
    ordem_servico_id: uuid.UUID | None = Query(default=None),
    tipo: TipoInspecao | None = Query(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    items, total = InspecaoService(db).list(
        page=page, page_size=page_size, aeronave_id=aeronave_id, ordem_servico_id=ordem_servico_id, tipo=tipo
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{inspecao_id}", response_model=InspecaoOut)
def get_inspecao(inspecao_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_consultar)):
    try:
        return InspecaoService(db).get(inspecao_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.put("/{inspecao_id}", response_model=InspecaoOut)
def update_inspecao(
    inspecao_id: uuid.UUID,
    data: InspecaoUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        return InspecaoService(db).update(inspecao_id, data)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.delete("/{inspecao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspecao(inspecao_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_excluir)):
    try:
        InspecaoService(db).delete(inspecao_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)
