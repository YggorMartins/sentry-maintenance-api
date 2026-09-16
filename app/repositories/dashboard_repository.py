from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.enums import StatusOS, TipoMovimentacao
from app.core.roles import UserRole
from app.models.aeronave import Aeronave
from app.models.agendamento import AgendamentoManutencao
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.models.ordem_servico import OrdemServico
from app.models.peca import Peca
from app.models.user import User


STATUS_ATIVOS = (StatusOS.ABERTA, StatusOS.EM_ANDAMENTO, StatusOS.AGUARDANDO_PECAS)


class DashboardRepository:
    """Consultas de leitura agregadas; evita N+1 e múltiplos round-trips do frontend."""

    def __init__(self, db: Session):
        self.db = db

    def resumo(self, inicio: datetime, fim: datetime) -> dict:
        duracao = fim - inicio
        inicio_anterior, fim_anterior = inicio - duracao, inicio
        agora = datetime.now(timezone.utc)

        def metricas_periodo(periodo_inicio, periodo_fim):
            return self.db.execute(
                select(
                    func.coalesce(func.sum(OrdemServico.custo_estimado), 0),
                    func.count(OrdemServico.id),
                ).where(
                    OrdemServico.data_abertura >= periodo_inicio,
                    OrdemServico.data_abertura < periodo_fim,
                    OrdemServico.status.in_(STATUS_ATIVOS),
                )
            ).one()

        custo, ativas = metricas_periodo(inicio, fim)
        custo_anterior, ativas_anterior = metricas_periodo(inicio_anterior, fim_anterior)

        criticas = self.db.scalar(
            select(func.count()).select_from(OrdemServico).where(
                OrdemServico.status.in_(STATUS_ATIVOS),
                OrdemServico.prazo.is_not(None),
                OrdemServico.prazo < agora,
            )
        ) or 0
        estoque_baixo = self.db.scalar(
            select(func.count()).select_from(Peca).where(Peca.quantidade_atual <= Peca.estoque_minimo)
        ) or 0
        previsao_falhas = self.db.scalar(
            select(func.count()).select_from(OrdemServico).where(
                OrdemServico.tipo_manutencao == "preditiva",
                OrdemServico.status.in_(STATUS_ATIVOS),
            )
        ) or 0

        ordens = self.db.execute(
            select(OrdemServico, Aeronave.prefixo, User.full_name)
            .join(Aeronave, Aeronave.id == OrdemServico.aeronave_id)
            .outerjoin(User, User.id == OrdemServico.mecanico_id)
            .where(OrdemServico.status.in_(STATUS_ATIVOS))
            .order_by(OrdemServico.prazo.asc().nulls_last(), OrdemServico.data_abertura.desc())
            .limit(10)
        ).all()

        categorias = self.db.execute(
            select(OrdemServico.categoria, func.count(OrdemServico.id))
            .where(OrdemServico.status.in_(STATUS_ATIVOS))
            .group_by(OrdemServico.categoria)
        ).all()
        total_categorias = sum(qtd for _, qtd in categorias)

        custo_pecas = self.db.scalar(
            select(func.coalesce(func.sum(MovimentacaoEstoque.quantidade * Peca.valor), 0))
            .join(Peca, Peca.id == MovimentacaoEstoque.peca_id)
            .where(
                MovimentacaoEstoque.tipo == TipoMovimentacao.SAIDA,
                MovimentacaoEstoque.data >= inicio,
                MovimentacaoEstoque.data < fim,
            )
        ) or 0
        horas = self.db.scalar(
            select(func.coalesce(func.sum(OrdemServico.horas_trabalhadas), 0)).where(
                OrdemServico.data_abertura >= inicio, OrdemServico.data_abertura < fim
            )
        ) or 0
        custo_mao_obra = float(horas) * 185.0

        def variacao(atual, anterior):
            return 0.0 if not anterior else round((float(atual) - float(anterior)) / float(anterior) * 100, 1)

        return {
            "periodo_inicio": inicio,
            "periodo_fim": fim,
            "kpis": {
                "custo_total": float(custo),
                "variacao_custo_percentual": variacao(custo, custo_anterior),
                "manutencoes_ativas": ativas,
                "variacao_ativas_percentual": variacao(ativas, ativas_anterior),
                "tarefas_criticas": criticas,
                "alertas_estoque": estoque_baixo,
                "previsao_falhas": previsao_falhas,
            },
            "ordens_ativas": [
                {
                    "id": ordem.id,
                    "numero": ordem.numero,
                    "ativo": prefixo,
                    "tipo": ordem.tipo_manutencao,
                    "categoria": ordem.categoria,
                    "responsavel": responsavel,
                    "status": ordem.status,
                    "custo_estimado": float(ordem.custo_estimado),
                    "prazo": ordem.prazo,
                }
                for ordem, prefixo, responsavel in ordens
            ],
            "distribuicao_categoria": [
                {
                    "categoria": categoria,
                    "quantidade": quantidade,
                    "percentual": round(quantidade / total_categorias * 100, 1) if total_categorias else 0,
                }
                for categoria, quantidade in categorias
            ],
            "composicao_custos": {
                "pecas": float(custo_pecas),
                "mao_de_obra": custo_mao_obra,
                "total": float(custo_pecas) + custo_mao_obra,
            },
        }

    def disponibilidade_tecnicos(self) -> list[dict]:
        agora = datetime.now(timezone.utc)
        limite = agora + timedelta(hours=8)
        ativos = (
            select(OrdemServico.mecanico_id, func.count().label("qtd"))
            .where(OrdemServico.status.in_(STATUS_ATIVOS))
            .group_by(OrdemServico.mecanico_id)
            .subquery()
        )
        proximos = (
            select(AgendamentoManutencao.tecnico_id, func.min(AgendamentoManutencao.inicio).label("proxima"))
            .where(AgendamentoManutencao.inicio >= agora)
            .group_by(AgendamentoManutencao.tecnico_id)
            .subquery()
        )
        rows = self.db.execute(
            select(User, func.coalesce(ativos.c.qtd, 0), proximos.c.proxima)
            .outerjoin(ativos, ativos.c.mecanico_id == User.id)
            .outerjoin(proximos, proximos.c.tecnico_id == User.id)
            .where(User.is_active.is_(True), User.role.in_((UserRole.MECANICO, UserRole.INSPETOR)))
            .order_by(User.full_name)
        ).all()
        return [
            {
                "id": user.id,
                "nome": user.full_name,
                "funcao": user.role.value,
                "disponivel": ordens == 0 and (proxima is None or proxima > limite),
                "ordens_ativas": ordens,
                "proxima_atividade": proxima,
            }
            for user, ordens, proxima in rows
        ]
