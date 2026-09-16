from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.roles import UserRole
from app.database.session import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.dashboard import DashboardResumo, DisponibilidadeTecnico
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
consultar = RoleChecker([UserRole.ADMIN, UserRole.INSPETOR, UserRole.MECANICO])


@router.get("/resumo", response_model=DashboardResumo)
def obter_resumo(
    inicio: datetime | None = Query(default=None),
    fim: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(consultar),
):
    agora = datetime.now(timezone.utc)
    fim = fim or agora
    inicio = inicio or (fim - timedelta(days=30))
    if fim <= inicio or fim - inicio > timedelta(days=366):
        raise HTTPException(status_code=422, detail="Período inválido; use no máximo 366 dias.")
    return DashboardService(db).resumo(inicio, fim)


@router.get("/tecnicos/disponibilidade", response_model=list[DisponibilidadeTecnico])
def listar_disponibilidade(
    db: Session = Depends(get_db), _: object = Depends(consultar)
):
    return DashboardService(db).disponibilidade_tecnicos()
