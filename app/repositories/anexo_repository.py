"""Repositório de Anexo."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import TipoEntidadeAnexo
from app.models.anexo import Anexo


class AnexoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, anexo_id: uuid.UUID) -> Anexo | None:
        return self.db.get(Anexo, anexo_id)

    def list(
        self,
        page: int,
        page_size: int,
        entidade_tipo: TipoEntidadeAnexo | None = None,
        entidade_id: uuid.UUID | None = None,
    ) -> tuple[list[Anexo], int]:
        base_stmt = select(Anexo)
        count_stmt = select(func.count()).select_from(Anexo)

        if entidade_tipo is not None:
            base_stmt = base_stmt.where(Anexo.entidade_tipo == entidade_tipo)
            count_stmt = count_stmt.where(Anexo.entidade_tipo == entidade_tipo)
        if entidade_id is not None:
            base_stmt = base_stmt.where(Anexo.entidade_id == entidade_id)
            count_stmt = count_stmt.where(Anexo.entidade_id == entidade_id)

        total = self.db.scalar(count_stmt) or 0
        stmt = base_stmt.order_by(Anexo.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(stmt)), total

    def create(self, anexo: Anexo) -> Anexo:
        self.db.add(anexo)
        self.db.commit()
        self.db.refresh(anexo)
        return anexo

    def delete(self, anexo: Anexo) -> None:
        self.db.delete(anexo)
        self.db.commit()
