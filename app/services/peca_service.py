"""Service de Peça — regra de negócio."""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import PecaAlreadyExistsError, PecaNotFoundError
from app.models.peca import Peca
from app.repositories.peca_repository import PecaRepository
from app.schemas.peca import PecaCreate, PecaUpdate


class PecaService:
    def __init__(self, db: Session):
        self.repository = PecaRepository(db)

    def create(self, data: PecaCreate) -> Peca:
        if self.repository.get_by_codigo(data.codigo) is not None:
            raise PecaAlreadyExistsError()
        return self.repository.create(data)

    def get(self, peca_id: uuid.UUID) -> Peca:
        peca = self.repository.get_by_id(peca_id)
        if peca is None:
            raise PecaNotFoundError()
        return peca

    def list(self, page: int, page_size: int) -> tuple[list[Peca], int]:
        return self.repository.list(page=page, page_size=page_size)

    def update(self, peca_id: uuid.UUID, data: PecaUpdate) -> Peca:
        peca = self.get(peca_id)
        existente = self.repository.get_by_codigo(data.codigo)
        if existente is not None and existente.id != peca_id:
            raise PecaAlreadyExistsError()
        return self.repository.update(peca, data)

    def delete(self, peca_id: uuid.UUID) -> None:
        peca = self.get(peca_id)
        self.repository.delete(peca)
