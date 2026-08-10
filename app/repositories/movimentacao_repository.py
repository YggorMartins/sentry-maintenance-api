"""
Repositório de Movimentação de Estoque.

`create()` faz DUAS escritas na mesma transação — ajusta
`Peca.quantidade_atual` e insere a linha de movimentação — com um
único commit. Se qualquer uma falhar, as duas são revertidas juntas
(o saldo da peça nunca fica dessincronizado do histórico).
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import TipoMovimentacao
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.models.peca import Peca
from app.schemas.movimentacao import MovimentacaoCreate


class MovimentacaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, movimentacao_id: uuid.UUID) -> MovimentacaoEstoque | None:
        return self.db.get(MovimentacaoEstoque, movimentacao_id)

    def list(
        self,
        page: int,
        page_size: int,
        peca_id: uuid.UUID | None = None,
        tipo: TipoMovimentacao | None = None,
        ordem_servico_id: uuid.UUID | None = None,
    ) -> tuple[list[MovimentacaoEstoque], int]:
        base_stmt = select(MovimentacaoEstoque)
        count_stmt = select(func.count()).select_from(MovimentacaoEstoque)

        if peca_id is not None:
            base_stmt = base_stmt.where(MovimentacaoEstoque.peca_id == peca_id)
            count_stmt = count_stmt.where(MovimentacaoEstoque.peca_id == peca_id)
        if tipo is not None:
            base_stmt = base_stmt.where(MovimentacaoEstoque.tipo == tipo)
            count_stmt = count_stmt.where(MovimentacaoEstoque.tipo == tipo)
        if ordem_servico_id is not None:
            base_stmt = base_stmt.where(MovimentacaoEstoque.ordem_servico_id == ordem_servico_id)
            count_stmt = count_stmt.where(MovimentacaoEstoque.ordem_servico_id == ordem_servico_id)

        total = self.db.scalar(count_stmt) or 0
        stmt = base_stmt.order_by(MovimentacaoEstoque.data.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(stmt)), total

    def create(self, peca: Peca, data: MovimentacaoCreate, usuario_id: uuid.UUID | None) -> MovimentacaoEstoque:
        if data.tipo == TipoMovimentacao.ENTRADA:
            peca.quantidade_atual += data.quantidade
        else:
            peca.quantidade_atual -= data.quantidade

        movimentacao = MovimentacaoEstoque(
            peca_id=peca.id,
            ordem_servico_id=data.ordem_servico_id,
            usuario_id=usuario_id,
            tipo=data.tipo,
            quantidade=data.quantidade,
            motivo=data.motivo,
        )
        self.db.add(peca)
        self.db.add(movimentacao)
        self.db.commit()
        self.db.refresh(movimentacao)
        return movimentacao
