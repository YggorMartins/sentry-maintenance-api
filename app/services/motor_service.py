"""Service de Motor — regra de negócio."""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import MotorAlreadyExistsError, MotorNotFoundError
from app.models.motor import Motor
from app.repositories.motor_repository import MotorRepository
from app.schemas.motor import MotorCreate, MotorUpdate


class MotorService:
    def __init__(self, db: Session):
        self.repository = MotorRepository(db)

    def create(self, data: MotorCreate) -> Motor:
        if self.repository.get_by_numero_serie(data.numero_serie) is not None:
            raise MotorAlreadyExistsError()
        return self.repository.create(data)

    def get(self, motor_id: uuid.UUID) -> Motor:
        motor = self.repository.get_by_id(motor_id)
        if motor is None:
            raise MotorNotFoundError()
        return motor

    def list(self, page: int, page_size: int) -> tuple[list[Motor], int]:
        return self.repository.list(page=page, page_size=page_size)

    def update(self, motor_id: uuid.UUID, data: MotorUpdate) -> Motor:
        motor = self.get(motor_id)
        existente = self.repository.get_by_numero_serie(data.numero_serie)
        if existente is not None and existente.id != motor_id:
            raise MotorAlreadyExistsError()
        return self.repository.update(motor, data)

    def delete(self, motor_id: uuid.UUID) -> None:
        motor = self.get(motor_id)
        self.repository.delete(motor)
