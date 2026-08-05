"""Repositório de Cliente — única camada que monta queries para `clientes`."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ClienteEmUsoError
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cliente_id: uuid.UUID) -> Cliente | None:
        return self.db.get(Cliente, cliente_id)

    def get_by_cpf(self, cpf: str) -> Cliente | None:
        return self.db.scalar(select(Cliente).where(Cliente.cpf == cpf))

    def get_by_cnpj(self, cnpj: str) -> Cliente | None:
        return self.db.scalar(select(Cliente).where(Cliente.cnpj == cnpj))

    def list(self, page: int, page_size: int) -> tuple[list[Cliente], int]:
        total = self.db.scalar(select(func.count()).select_from(Cliente)) or 0
        stmt = (
            select(Cliente)
            .order_by(Cliente.nome)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt))
        return items, total

    def create(self, data: ClienteCreate) -> Cliente:
        cliente = Cliente(**data.model_dump())
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def update(self, cliente: Cliente, data: ClienteUpdate) -> Cliente:
        for field, value in data.model_dump().items():
            setattr(cliente, field, value)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def delete(self, cliente: Cliente) -> None:
        self.db.delete(cliente)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ClienteEmUsoError()
