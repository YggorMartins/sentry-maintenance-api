"""Router de Movimentação de Estoque — endpoints REST."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.enums import TipoMovimentacao
from app.core.exceptions import (
    EstoqueInsuficienteError,
    OrdemServicoNotFoundError,
    PecaNotFoundError,
)
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoOut
from app.services.movimentacao_service import MovimentacaoService

router = APIRouter(prefix="/movimentacoes-estoque", tags=["Estoque"])

pode_consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
pode_movimentar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])


def _tratar_erros_de_negocio(exc: Exception):
    if isinstance(exc, PecaNotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Peça informada não existe.")
    if isinstance(exc, OrdemServicoNotFoundError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ordem de serviço informada não existe.")
    if isinstance(exc, EstoqueInsuficienteError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Quantidade em estoque insuficiente para esta saída.",
        )
    raise exc


@router.post("", response_model=MovimentacaoOut, status_code=status.HTTP_201_CREATED)
def create_movimentacao(
    data: MovimentacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(pode_movimentar),
):
    try:
        return MovimentacaoService(db).create(data, usuario_id=current_user.id)
    except Exception as exc:
        _tratar_erros_de_negocio(exc)


@router.get("", response_model=PaginatedResponse[MovimentacaoOut])
def list_movimentacoes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    peca_id: uuid.UUID | None = Query(default=None),
    tipo: TipoMovimentacao | None = Query(default=None),
    ordem_servico_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(pode_consultar),
):
    items, total = MovimentacaoService(db).list(
        page=page, page_size=page_size, peca_id=peca_id, tipo=tipo, ordem_servico_id=ordem_servico_id
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)
