import uuid
from datetime import datetime

from pydantic import BaseModel

from app.core.enums import CategoriaManutencao, StatusOS, TipoManutencao


class KpisDashboard(BaseModel):
    custo_total: float
    variacao_custo_percentual: float
    manutencoes_ativas: int
    variacao_ativas_percentual: float
    tarefas_criticas: int
    alertas_estoque: int
    previsao_falhas: int


class OrdemAtivaDashboard(BaseModel):
    id: uuid.UUID
    numero: str
    ativo: str
    tipo: TipoManutencao
    categoria: CategoriaManutencao
    responsavel: str | None
    status: StatusOS
    custo_estimado: float
    prazo: datetime | None


class CategoriaDashboard(BaseModel):
    categoria: CategoriaManutencao
    quantidade: int
    percentual: float


class CustosDashboard(BaseModel):
    pecas: float
    mao_de_obra: float
    total: float


class DashboardResumo(BaseModel):
    periodo_inicio: datetime
    periodo_fim: datetime
    kpis: KpisDashboard
    ordens_ativas: list[OrdemAtivaDashboard]
    distribuicao_categoria: list[CategoriaDashboard]
    composicao_custos: CustosDashboard


class DisponibilidadeTecnico(BaseModel):
    id: uuid.UUID
    nome: str
    funcao: str
    disponivel: bool
    ordens_ativas: int
    proxima_atividade: datetime | None
