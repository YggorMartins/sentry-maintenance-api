"""Router de Peça — endpoints REST."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import PecaAlreadyExistsError, PecaEmUsoError, PecaNotFoundError
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.common import PaginatedResponse
from app.schemas.peca import PecaCreate, PecaOut, PecaUpdate
from app.services.peca_service import PecaService

router = APIRouter(prefix="/pecas", tags=["Peças"])

pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_gerenciar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_excluir = RoleChecker([UserRole.ADMIN])


@router.post("", response_model=PecaOut, status_code=status.HTTP_201_CREATED)
def create_peca(data: PecaCreate, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)):
    try:
        return PecaService(db).create(data)
    except PecaAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Já existe uma peça cadastrada com este código."
        )


@router.get("", response_model=PaginatedResponse[PecaOut])
def list_pecas(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    items, total = PecaService(db).list(page=page, page_size=page_size)
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{peca_id}", response_model=PecaOut)
def get_peca(peca_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_consultar)):
    try:
        return PecaService(db).get(peca_id)
    except PecaNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peça não encontrada.")


@router.put("/{peca_id}", response_model=PecaOut)
def update_peca(
    peca_id: uuid.UUID, data: PecaUpdate, db: Session = Depends(get_db), _: object = Depends(pode_gerenciar)
):
    try:
        return PecaService(db).update(peca_id, data)
    except PecaNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peça não encontrada.")
    except PecaAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Já existe outra peça cadastrada com este código."
        )


@router.delete("/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_peca(peca_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(pode_excluir)):
    try:
        PecaService(db).delete(peca_id)
    except PecaNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peça não encontrada.")
    except PecaEmUsoError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Peça possui movimentações de estoque e não pode ser removida.",
        )
