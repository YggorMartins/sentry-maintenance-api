"""Repositório de Aeronave."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.aeronave import Aeronave
from app.schemas.aeronave import AeronaveCreate, AeronaveUpdate


class AeronaveRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, aeronave_id: uuid.UUID) -> Aeronave | None:
        stmt = select(Aeronave).options(joinedload(Aeronave.motor)).where(Aeronave.id == aeronave_id)
        return self.db.scalar(stmt)

    def get_by_prefixo(self, prefixo: str) -> Aeronave | None:
        return self.db.scalar(select(Aeronave).where(Aeronave.prefixo == prefixo))

    def get_by_numero_serie(self, numero_serie: str) -> Aeronave | None:
        return self.db.scalar(select(Aeronave).where(Aeronave.numero_serie == numero_serie))

    def get_by_motor_id(self, motor_id: uuid.UUID) -> Aeronave | None:
        return self.db.scalar(select(Aeronave).where(Aeronave.motor_id == motor_id))

    def list(self, page: int, page_size: int, cliente_id: uuid.UUID | None = None) -> tuple[list[Aeronave], int]:
        base_stmt = select(Aeronave)
        count_stmt = select(func.count()).select_from(Aeronave)
        if cliente_id is not None:
            base_stmt = base_stmt.where(Aeronave.cliente_id == cliente_id)
            count_stmt = count_stmt.where(Aeronave.cliente_id == cliente_id)

        total = self.db.scalar(count_stmt) or 0
        stmt = (
            base_stmt.options(joinedload(Aeronave.motor))
            .order_by(Aeronave.prefixo)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).unique()), total

    def create(self, data: AeronaveCreate) -> Aeronave:
        aeronave = Aeronave(**data.model_dump())
        self.db.add(aeronave)
        self.db.commit()
        self.db.refresh(aeronave)
        return aeronave

    def update(self, aeronave: Aeronave, data: AeronaveUpdate) -> Aeronave:
        for field, value in data.model_dump().items():
            setattr(aeronave, field, value)
        self.db.commit()
        self.db.refresh(aeronave)
        return aeronave

    def delete(self, aeronave: Aeronave) -> None:
        self.db.delete(aeronave)
        self.db.commit()
