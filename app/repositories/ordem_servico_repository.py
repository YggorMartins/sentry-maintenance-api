"""Repositório de Ordem de Serviço."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.enums import StatusOS
from app.models.ordem_servico import OrdemServico
from app.schemas.ordem_servico import OrdemServicoCreate, OrdemServicoUpdate


class OrdemServicoRepository:
    def __init__(self, db: Session):
        self.db = db

    def _proximo_numero(self) -> str:
        """
        Usa a SEQUENCE nativa do Postgres (criada na migration) para
        gerar o número de forma atômica, mesmo sob requisições
        concorrentes — ver explicação completa na conversa da Etapa 4.
        """
        valor = self.db.execute(text("SELECT nextval('os_numero_seq')")).scalar_one()
        return f"OS-{valor:06d}"

    def get_by_id(self, os_id: uuid.UUID) -> OrdemServico | None:
        return self.db.get(OrdemServico, os_id)

    def list(
        self,
        page: int,
        page_size: int,
        aeronave_id: uuid.UUID | None = None,
        status_filtro: StatusOS | None = None,
        mecanico_id: uuid.UUID | None = None,
    ) -> tuple[list[OrdemServico], int]:
        base_stmt = select(OrdemServico)
        count_stmt = select(func.count()).select_from(OrdemServico)

        if aeronave_id is not None:
            base_stmt = base_stmt.where(OrdemServico.aeronave_id == aeronave_id)
            count_stmt = count_stmt.where(OrdemServico.aeronave_id == aeronave_id)
        if status_filtro is not None:
            base_stmt = base_stmt.where(OrdemServico.status == status_filtro)
            count_stmt = count_stmt.where(OrdemServico.status == status_filtro)
        if mecanico_id is not None:
            base_stmt = base_stmt.where(OrdemServico.mecanico_id == mecanico_id)
            count_stmt = count_stmt.where(OrdemServico.mecanico_id == mecanico_id)

        total = self.db.scalar(count_stmt) or 0
        stmt = (
            base_stmt.order_by(OrdemServico.data_abertura.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt)), total

    def create(self, data: OrdemServicoCreate) -> OrdemServico:
        ordem = OrdemServico(
            **data.model_dump(),
            numero=self._proximo_numero(),
            data_abertura=datetime.now(timezone.utc),
            status=StatusOS.ABERTA,
        )
        self.db.add(ordem)
        self.db.commit()
        self.db.refresh(ordem)
        return ordem

    def update(self, ordem: OrdemServico, data: OrdemServicoUpdate) -> OrdemServico:
        for field, value in data.model_dump().items():
            setattr(ordem, field, value)
        self.db.commit()
        self.db.refresh(ordem)
        return ordem

    def update_status(self, ordem: OrdemServico, novo_status: StatusOS) -> OrdemServico:
        ordem.status = novo_status
        if novo_status in (StatusOS.CONCLUIDA, StatusOS.CANCELADA):
            ordem.data_fechamento = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(ordem)
        return ordem

    def delete(self, ordem: OrdemServico) -> None:
        self.db.delete(ordem)
        self.db.commit()
