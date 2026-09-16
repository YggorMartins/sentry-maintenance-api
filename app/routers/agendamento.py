import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import AeronaveNotFoundError, AgendamentoNotFoundError, ResponsavelInvalidoError
from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.agendamento import AgendamentoCreate, AgendamentoOut, AgendamentoUpdate
from app.schemas.common import PaginatedResponse
from app.services.agendamento_service import AgendamentoService

router = APIRouter(prefix="/agendamentos", tags=["Agenda de manutenção"])
consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])
gerenciar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR])


@router.get("", response_model=PaginatedResponse[AgendamentoOut])
def listar_agendamentos(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    inicio: datetime | None = None,
    fim: datetime | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(consultar),
):
    items, total = AgendamentoService(db).list(page, page_size, inicio, fim)
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=AgendamentoOut, status_code=status.HTTP_201_CREATED)
def criar_agendamento(data: AgendamentoCreate, db: Session = Depends(get_db), _: object = Depends(gerenciar)):
    try:
        return AgendamentoService(db).create(data)
    except AeronaveNotFoundError:
        raise HTTPException(status_code=404, detail="Aeronave não encontrada.")
    except ResponsavelInvalidoError:
        raise HTTPException(status_code=422, detail="Técnico inválido ou inativo.")


@router.put("/{agendamento_id}", response_model=AgendamentoOut)
def atualizar_agendamento(
    agendamento_id: uuid.UUID,
    data: AgendamentoUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(gerenciar),
):
    try:
        return AgendamentoService(db).update(agendamento_id, data)
    except AgendamentoNotFoundError:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    except ResponsavelInvalidoError:
        raise HTTPException(status_code=422, detail="Técnico inválido ou inativo.")


@router.delete("/{agendamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_agendamento(
    agendamento_id: uuid.UUID, db: Session = Depends(get_db), _: object = Depends(gerenciar)
):
    try:
        AgendamentoService(db).delete(agendamento_id)
    except AgendamentoNotFoundError:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
