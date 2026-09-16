import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import AeronaveNotFoundError, AgendamentoNotFoundError, ResponsavelInvalidoError
from app.core.roles import UserRole
from app.repositories.aeronave_repository import AeronaveRepository
from app.repositories.agendamento_repository import AgendamentoRepository
from app.repositories.user_repository import UserRepository
from app.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate


class AgendamentoService:
    def __init__(self, db: Session):
        self.repository = AgendamentoRepository(db)
        self.aeronaves = AeronaveRepository(db)
        self.usuarios = UserRepository(db)

    def _validar_referencias(self, aeronave_id, tecnico_id) -> None:
        if self.aeronaves.get_by_id(aeronave_id) is None:
            raise AeronaveNotFoundError()
        if tecnico_id:
            tecnico = self.usuarios.get_by_id(tecnico_id)
            if tecnico is None or not tecnico.is_active or tecnico.role not in {
                UserRole.MECANICO, UserRole.INSPETOR
            }:
                raise ResponsavelInvalidoError()

    def list(self, page: int, page_size: int, inicio: datetime | None, fim: datetime | None):
        return self.repository.list(page, page_size, inicio, fim)

    def create(self, data: AgendamentoCreate):
        self._validar_referencias(data.aeronave_id, data.tecnico_id)
        return self.repository.create(data)

    def update(self, item_id: uuid.UUID, data: AgendamentoUpdate):
        item = self.repository.get_by_id(item_id)
        if item is None:
            raise AgendamentoNotFoundError()
        self._validar_referencias(item.aeronave_id, data.tecnico_id)
        return self.repository.update(item, data)

    def delete(self, item_id: uuid.UUID) -> None:
        item = self.repository.get_by_id(item_id)
        if item is None:
            raise AgendamentoNotFoundError()
        self.repository.delete(item)
