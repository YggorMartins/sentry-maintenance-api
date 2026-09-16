import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agendamento import AgendamentoManutencao
from app.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate


class AgendamentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, agendamento_id: uuid.UUID) -> AgendamentoManutencao | None:
        return self.db.get(AgendamentoManutencao, agendamento_id)

    def list(
        self, page: int, page_size: int, inicio: datetime | None, fim: datetime | None
    ) -> tuple[list[AgendamentoManutencao], int]:
        filtros = []
        if inicio is not None:
            filtros.append(AgendamentoManutencao.fim >= inicio)
        if fim is not None:
            filtros.append(AgendamentoManutencao.inicio <= fim)
        total = self.db.scalar(
            select(func.count()).select_from(AgendamentoManutencao).where(*filtros)
        ) or 0
        stmt = (
            select(AgendamentoManutencao)
            .where(*filtros)
            .order_by(AgendamentoManutencao.inicio)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt)), total

    def create(self, data: AgendamentoCreate) -> AgendamentoManutencao:
        item = AgendamentoManutencao(**data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: AgendamentoManutencao, data: AgendamentoUpdate) -> AgendamentoManutencao:
        for field, value in data.model_dump().items():
            setattr(item, field, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: AgendamentoManutencao) -> None:
        self.db.delete(item)
        self.db.commit()
