"""Router de Cliente — endpoints REST, sem regra de negócio."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import ClienteAlreadyExistsError, ClienteEmUsoError, ClienteNotFoundError
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.schemas.common import PaginatedResponse
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# Consultar clientes: admin, inspetor e mecânico (precisam ver o dono da
# aeronave ao trabalhar numa Ordem de Serviço).
pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
# Gerenciar (criar/editar/excluir) clientes: só admin e inspetor.
pode_gerenciar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR])


@router.post("", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def create_cliente(
    data: ClienteCreate,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        return ClienteService(db).create(data)
    except ClienteAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente cadastrado com este CPF/CNPJ.",
        )


@router.get("", response_model=PaginatedResponse[ClienteOut])
def list_clientes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    items, total = ClienteService(db).list(page=page, page_size=page_size)
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{cliente_id}", response_model=ClienteOut)
def get_cliente(
    cliente_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    try:
        return ClienteService(db).get(cliente_id)
    except ClienteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")


@router.put("/{cliente_id}", response_model=ClienteOut)
def update_cliente(
    cliente_id: uuid.UUID,
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        return ClienteService(db).update(cliente_id, data)
    except ClienteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    except ClienteAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outro cliente cadastrado com este CPF/CNPJ.",
        )


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(
    cliente_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: object = Depends(pode_gerenciar),
):
    try:
        ClienteService(db).delete(cliente_id)
    except ClienteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    except ClienteEmUsoError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cliente possui aeronaves vinculadas e não pode ser removido.",
        )
