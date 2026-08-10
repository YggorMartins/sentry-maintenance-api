"""
Service de Movimentação de Estoque.

Regra central: uma SAÍDA nunca pode deixar `quantidade_atual` negativo.
"""
import uuid

from sqlalchemy.orm import Session

from app.core.enums import TipoMovimentacao
from app.core.exceptions import (
    EstoqueInsuficienteError,
    OrdemServicoNotFoundError,
    PecaNotFoundError,
)
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.repositories.peca_repository import PecaRepository
from app.schemas.movimentacao import MovimentacaoCreate


class MovimentacaoService:
    def __init__(self, db: Session):
        self.repository = MovimentacaoRepository(db)
        self.pecas = PecaRepository(db)
        self.ordens_servico = OrdemServicoRepository(db)

    def create(self, data: MovimentacaoCreate, usuario_id: uuid.UUID | None) -> MovimentacaoEstoque:
        peca = self.pecas.get_by_id(data.peca_id)
        if peca is None:
            raise PecaNotFoundError()

        if data.ordem_servico_id is not None and self.ordens_servico.get_by_id(data.ordem_servico_id) is None:
            raise OrdemServicoNotFoundError()

        if data.tipo == TipoMovimentacao.SAIDA and data.quantidade > peca.quantidade_atual:
            raise EstoqueInsuficienteError()

        return self.repository.create(peca, data, usuario_id)

    def list(
        self,
        page: int,
        page_size: int,
        peca_id: uuid.UUID | None = None,
        tipo: TipoMovimentacao | None = None,
        ordem_servico_id: uuid.UUID | None = None,
    ) -> tuple[list[MovimentacaoEstoque], int]:
        return self.repository.list(
            page=page, page_size=page_size, peca_id=peca_id, tipo=tipo, ordem_servico_id=ordem_servico_id
        )
