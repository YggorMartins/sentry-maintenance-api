"""
Service de Ordem de Serviço.

Contém a máquina de estados do campo `status` e as validações de
integridade (aeronave/motor existem, mecânico/inspetor têm o papel
correto) antes de qualquer escrita no banco.
"""
import uuid

from sqlalchemy.orm import Session

from app.core.enums import StatusOS
from app.core.roles import UserRole
from app.core.exceptions import (
    AeronaveNotFoundError,
    MotorNotFoundError,
    OrdemServicoNaoEditavelError,
    OrdemServicoNotFoundError,
    ResponsavelInvalidoError,
    TransicaoStatusInvalidaError,
)
from app.models.ordem_servico import OrdemServico
from app.repositories.aeronave_repository import AeronaveRepository
from app.repositories.motor_repository import MotorRepository
from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.repositories.user_repository import UserRepository
from app.schemas.ordem_servico import OrdemServicoCreate, OrdemServicoUpdate

# Estados terminais: uma vez atingidos, a OS não aceita mais edição nem
# nova transição de status.
ESTADOS_TERMINAIS = {StatusOS.CONCLUIDA, StatusOS.CANCELADA}

# Tabela de transições permitidas: de onde -> para onde.
TRANSICOES_PERMITIDAS: dict[StatusOS, set[StatusOS]] = {
    StatusOS.ABERTA: {StatusOS.EM_ANDAMENTO, StatusOS.CANCELADA},
    StatusOS.EM_ANDAMENTO: {StatusOS.AGUARDANDO_PECAS, StatusOS.CONCLUIDA, StatusOS.CANCELADA},
    StatusOS.AGUARDANDO_PECAS: {StatusOS.EM_ANDAMENTO, StatusOS.CANCELADA},
    StatusOS.CONCLUIDA: set(),
    StatusOS.CANCELADA: set(),
}


class OrdemServicoService:
    def __init__(self, db: Session):
        self.repository = OrdemServicoRepository(db)
        self.aeronaves = AeronaveRepository(db)
        self.motores = MotorRepository(db)
        self.users = UserRepository(db)

    def _validar_responsaveis(
        self, mecanico_id: uuid.UUID | None, inspetor_id: uuid.UUID | None, motor_id: uuid.UUID | None
    ) -> None:
        if motor_id is not None and self.motores.get_by_id(motor_id) is None:
            raise MotorNotFoundError()

        if mecanico_id is not None:
            mecanico = self.users.get_by_id(mecanico_id)
            if mecanico is None or mecanico.role != UserRole.MECANICO:
                raise ResponsavelInvalidoError()

        if inspetor_id is not None:
            inspetor = self.users.get_by_id(inspetor_id)
            if inspetor is None or inspetor.role != UserRole.INSPETOR:
                raise ResponsavelInvalidoError()

    def create(self, data: OrdemServicoCreate) -> OrdemServico:
        if self.aeronaves.get_by_id(data.aeronave_id) is None:
            raise AeronaveNotFoundError()
        self._validar_responsaveis(data.mecanico_id, data.inspetor_id, data.motor_id)
        return self.repository.create(data)

    def get(self, os_id: uuid.UUID) -> OrdemServico:
        ordem = self.repository.get_by_id(os_id)
        if ordem is None:
            raise OrdemServicoNotFoundError()
        return ordem

    def list(
        self,
        page: int,
        page_size: int,
        aeronave_id: uuid.UUID | None = None,
        status_filtro: StatusOS | None = None,
        mecanico_id: uuid.UUID | None = None,
    ) -> tuple[list[OrdemServico], int]:
        return self.repository.list(
            page=page,
            page_size=page_size,
            aeronave_id=aeronave_id,
            status_filtro=status_filtro,
            mecanico_id=mecanico_id,
        )

    def update(self, os_id: uuid.UUID, data: OrdemServicoUpdate) -> OrdemServico:
        ordem = self.get(os_id)
        if ordem.status in ESTADOS_TERMINAIS:
            raise OrdemServicoNaoEditavelError()
        self._validar_responsaveis(data.mecanico_id, data.inspetor_id, data.motor_id)
        return self.repository.update(ordem, data)

    def update_status(self, os_id: uuid.UUID, novo_status: StatusOS) -> OrdemServico:
        ordem = self.get(os_id)
        permitidos = TRANSICOES_PERMITIDAS.get(ordem.status, set())
        if novo_status not in permitidos:
            raise TransicaoStatusInvalidaError()
        return self.repository.update_status(ordem, novo_status)

    def delete(self, os_id: uuid.UUID) -> None:
        ordem = self.get(os_id)
        if ordem.status != StatusOS.ABERTA:
            # Preserva histórico/auditoria: só é permitido excluir uma OS
            # que ainda não teve nenhum trabalho iniciado.
            raise OrdemServicoNaoEditavelError()
        self.repository.delete(ordem)
