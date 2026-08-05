"""Router de Aeronave — endpoints REST."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AeronaveAlreadyExistsError,
    AeronaveNotFoundError,
    MotorJaInstaladoError,
    MotorNotFoundError,
    ProprietarioNotFoundError,
)
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.aeronave import AeronaveCreate, AeronaveOut, AeronaveUpdate
from app.schemas.common import PaginatedResponse
from app.services.aeronave_service import AeronaveService

router = APIRouter(prefix="/aeronaves", tags=["Aeronaves"])

pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_gerenciar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR])


def _tratar_erros_de_negocio(exc: Exception):
    if isinstance(exc, AeronaveNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aeronave não encontrada.")
    if isinstance(exc, AeronaveAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma aeronave cadastrada com este prefixo ou número de série.",
        )
    if isinstance(exc, ProprietarioNotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cliente (proprietário) informado não existe.")
    if isinstance(exc, MotorNotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Motor informado não existe.")
    if isinstance(exc, MotorJaInstaladoError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O motor informado já está instalado em outra aeronave.",
        )
    raise exc


@router.post("", response_model=AeronaveOut, status_code=status.HTTP_201_CREATED)
def create_aeronave(data: AeronaveCreate, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)):
    try:
        return AeronaveService(db).create(data)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.get("", response_model=PaginatedResponse[AeronaveOut])
def list_aeronaves(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    cliente_id: uuid.UUID | None = Query(default=None, description="Filtrar por proprietário"),
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    items, total = AeronaveService(db).list(page=page, page_size=page_size, cliente_id=cliente_id)
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{aeronave_id}", response_model=AeronaveOut)
def get_aeronave(aeronave_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_consultar)):
    try:
        return AeronaveService(db).get(aeronave_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.put("/{aeronave_id}", response_model=AeronaveOut)
def update_aeronave(
    aeronave_id: uuid.UUID,
    data: AeronaveUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        return AeronaveService(db).update(aeronave_id, data)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.delete("/{aeronave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aeronave(aeronave_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)):
    try:
        AeronaveService(db).delete(aeronave_id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)
