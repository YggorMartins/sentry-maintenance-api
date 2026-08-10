"""Repositório de Peça."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import PecaEmUsoError
from app.models.peca import Peca
from app.schemas.peca import PecaCreate, PecaUpdate


class PecaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, peca_id: uuid.UUID) -> Peca | None:
        return self.db.get(Peca, peca_id)

    def get_by_codigo(self, codigo: str) -> Peca | None:
        return self.db.scalar(select(Peca).where(Peca.codigo == codigo))

    def list(self, page: int, page_size: int) -> tuple[list[Peca], int]:
        total = self.db.scalar(select(func.count()).select_from(Peca)) or 0
        stmt = select(Peca).order_by(Peca.codigo).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(stmt)), total

    def create(self, data: PecaCreate) -> Peca:
        peca = Peca(**data.model_dump())
        self.db.add(peca)
        self.db.commit()
        self.db.refresh(peca)
        return peca

    def update(self, peca: Peca, data: PecaUpdate) -> Peca:
        for field, value in data.model_dump().items():
            setattr(peca, field, value)
        self.db.commit()
        self.db.refresh(peca)
        return peca

    def delete(self, peca: Peca) -> None:
        self.db.delete(peca)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise PecaEmUsoError()
