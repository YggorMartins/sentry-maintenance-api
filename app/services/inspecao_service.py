"""
Service de Inspeção.

Valida que a OS referenciada existe e que o responsável é de fato um
Inspetor (não basta o ID existir — precisa ter o papel certo).
"""
import uuid

from sqlalchemy.orm import Session

from app.core.enums import TipoInspecao
from app.core.exceptions import (
    InspecaoNotFoundError,
    OrdemServicoNotFoundError,
    ResponsavelInvalidoError,
)
from app.core.roles import UserRole
from app.models.inspecao import Inspecao
from app.repositories.inspecao_repository import InspecaoRepository
from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.repositories.user_repository import UserRepository
from app.schemas.inspecao import InspecaoCreate, InspecaoUpdate


class InspecaoService:
    def __init__(self, db: Session):
        self.repository = InspecaoRepository(db)
        self.ordens_servico = OrdemServicoRepository(db)
        self.users = UserRepository(db)

    def _validar(self, data: InspecaoCreate | InspecaoUpdate) -> None:
        if self.ordens_servico.get_by_id(data.ordem_servico_id) is None:
            raise OrdemServicoNotFoundError()

        responsavel = self.users.get_by_id(data.responsavel_id)
        if responsavel is None or responsavel.role != UserRole.INSPETOR:
            raise ResponsavelInvalidoError()

    def create(self, data: InspecaoCreate) -> Inspecao:
        self._validar(data)
        return self.repository.create(data)

    def get(self, inspecao_id: uuid.UUID) -> Inspecao:
        inspecao = self.repository.get_by_id(inspecao_id)
        if inspecao is None:
            raise InspecaoNotFoundError()
        return inspecao

    def list(
        self,
        page: int,
        page_size: int,
        aeronave_id: uuid.UUID | None = None,
        ordem_servico_id: uuid.UUID | None = None,
        tipo: TipoInspecao | None = None,
    ) -> tuple[list[Inspecao], int]:
        return self.repository.list(
            page=page, page_size=page_size, aeronave_id=aeronave_id, ordem_servico_id=ordem_servico_id, tipo=tipo
        )

    def update(self, inspecao_id: uuid.UUID, data: InspecaoUpdate) -> Inspecao:
        inspecao = self.get(inspecao_id)
        self._validar(data)
        return self.repository.update(inspecao, data)

    def delete(self, inspecao_id: uuid.UUID) -> None:
        inspecao = self.get(inspecao_id)
        self.repository.delete(inspecao)
