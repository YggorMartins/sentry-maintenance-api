"""Repositório de Inspeção."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import TipoInspecao
from app.models.inspecao import Inspecao
from app.models.ordem_servico import OrdemServico
from app.schemas.inspecao import InspecaoCreate, InspecaoUpdate


class InspecaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, inspecao_id: uuid.UUID) -> Inspecao | None:
        return self.db.get(Inspecao, inspecao_id)

    def list(
        self,
        page: int,
        page_size: int,
        aeronave_id: uuid.UUID | None = None,
        ordem_servico_id: uuid.UUID | None = None,
        tipo: TipoInspecao | None = None,
    ) -> tuple[list[Inspecao], int]:
        base_stmt = select(Inspecao)
        count_stmt = select(func.count()).select_from(Inspecao)

        if aeronave_id is not None:
            base_stmt = base_stmt.join(OrdemServico).where(OrdemServico.aeronave_id == aeronave_id)
            count_stmt = count_stmt.join(OrdemServico).where(OrdemServico.aeronave_id == aeronave_id)
        if ordem_servico_id is not None:
            base_stmt = base_stmt.where(Inspecao.ordem_servico_id == ordem_servico_id)
            count_stmt = count_stmt.where(Inspecao.ordem_servico_id == ordem_servico_id)
        if tipo is not None:
            base_stmt = base_stmt.where(Inspecao.tipo == tipo)
            count_stmt = count_stmt.where(Inspecao.tipo == tipo)

        total = self.db.scalar(count_stmt) or 0
        stmt = base_stmt.order_by(Inspecao.data.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(stmt)), total

    def create(self, data: InspecaoCreate) -> Inspecao:
        inspecao = Inspecao(**data.model_dump())
        self.db.add(inspecao)
        self.db.commit()
        self.db.refresh(inspecao)
        return inspecao

    def update(self, inspecao: Inspecao, data: InspecaoUpdate) -> Inspecao:
        for field, value in data.model_dump().items():
            setattr(inspecao, field, value)
        self.db.commit()
        self.db.refresh(inspecao)
        return inspecao

    def delete(self, inspecao: Inspecao) -> None:
        self.db.delete(inspecao)
        self.db.commit()
