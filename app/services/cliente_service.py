"""
Service de Cliente.

Regra de negócio: impedir duplicidade de CPF/CNPJ (a unicidade também
existe no banco como rede de segurança, mas aqui detectamos ANTES de
tentar o INSERT, para devolver uma mensagem de erro clara em vez de
deixar estourar um erro genérico de constraint do banco).
"""
import uuid

from sqlalchemy.orm import Session

from app.core.enums import TipoPessoa
from app.core.exceptions import ClienteAlreadyExistsError, ClienteNotFoundError
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.cliente import ClienteCreate, ClienteUpdate


class ClienteService:
    def __init__(self, db: Session):
        self.repository = ClienteRepository(db)

    def _checar_duplicidade(self, data: ClienteCreate | ClienteUpdate, ignorar_id: uuid.UUID | None = None) -> None:
        existente = None
        if data.tipo_pessoa == TipoPessoa.FISICA and data.cpf:
            existente = self.repository.get_by_cpf(data.cpf)
        elif data.tipo_pessoa == TipoPessoa.JURIDICA and data.cnpj:
            existente = self.repository.get_by_cnpj(data.cnpj)

        if existente is not None and existente.id != ignorar_id:
            raise ClienteAlreadyExistsError()

    def create(self, data: ClienteCreate) -> Cliente:
        self._checar_duplicidade(data)
        return self.repository.create(data)

    def get(self, cliente_id: uuid.UUID) -> Cliente:
        cliente = self.repository.get_by_id(cliente_id)
        if cliente is None:
            raise ClienteNotFoundError()
        return cliente

    def list(self, page: int, page_size: int) -> tuple[list[Cliente], int]:
        return self.repository.list(page=page, page_size=page_size)

    def update(self, cliente_id: uuid.UUID, data: ClienteUpdate) -> Cliente:
        cliente = self.get(cliente_id)
        self._checar_duplicidade(data, ignorar_id=cliente_id)
        return self.repository.update(cliente, data)

    def delete(self, cliente_id: uuid.UUID) -> None:
        cliente = self.get(cliente_id)
        self.repository.delete(cliente)
