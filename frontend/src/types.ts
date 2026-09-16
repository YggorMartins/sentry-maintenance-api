export type StatusOS = 'aberta' | 'em_andamento' | 'aguardando_pecas' | 'concluida' | 'cancelada'
export type Categoria = 'avionicos' | 'mecanica' | 'estrutura' | 'motor'

export interface DashboardData {
  periodo_inicio: string
  periodo_fim: string
  kpis: {
    custo_total: number; variacao_custo_percentual: number; manutencoes_ativas: number
    variacao_ativas_percentual: number; tarefas_criticas: number; alertas_estoque: number; previsao_falhas: number
  }
  ordens_ativas: Array<{
    id: string; numero: string; ativo: string; tipo: string; categoria: Categoria
    responsavel: string | null; status: StatusOS; custo_estimado: number; prazo: string | null
  }>
  distribuicao_categoria: Array<{ categoria: Categoria; quantidade: number; percentual: number }>
  composicao_custos: { pecas: number; mao_de_obra: number; total: number }
}
