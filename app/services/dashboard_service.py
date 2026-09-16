from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def resumo(self, inicio: datetime, fim: datetime):
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        if fim.tzinfo is None:
            fim = fim.replace(tzinfo=timezone.utc)
        return self.repository.resumo(inicio, fim)

    def disponibilidade_tecnicos(self):
        return self.repository.disponibilidade_tecnicos()
