"""Repositório de Motor."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.motor import Motor
from app.schemas.motor import MotorCreate, MotorUpdate


class MotorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, motor_id: uuid.UUID) -> Motor | None:
        return self.db.get(Motor, motor_id)

    def get_by_numero_serie(self, numero_serie: str) -> Motor | None:
        return self.db.scalar(select(Motor).where(Motor.numero_serie == numero_serie))

    def list(self, page: int, page_size: int) -> tuple[list[Motor], int]:
        total = self.db.scalar(select(func.count()).select_from(Motor)) or 0
        stmt = (
            select(Motor)
            .order_by(Motor.fabricante, Motor.modelo)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt)), total

    def create(self, data: MotorCreate) -> Motor:
        motor = Motor(**data.model_dump())
        self.db.add(motor)
        self.db.commit()
        self.db.refresh(motor)
        return motor

    def update(self, motor: Motor, data: MotorUpdate) -> Motor:
        for field, value in data.model_dump().items():
            setattr(motor, field, value)
        self.db.commit()
        self.db.refresh(motor)
        return motor

    def delete(self, motor: Motor) -> None:
        self.db.delete(motor)
        self.db.commit()
