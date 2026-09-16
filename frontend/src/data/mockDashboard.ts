import type { DashboardData } from '../types'

export const mockDashboard: DashboardData = {
  periodo_inicio: '2026-09-01T00:00:00Z', periodo_fim: '2026-09-30T23:59:59Z',
  kpis: { custo_total: 184250.8, variacao_custo_percentual: 12.4, manutencoes_ativas: 28, variacao_ativas_percentual: 8.2, tarefas_criticas: 7, alertas_estoque: 12, previsao_falhas: 4 },
  ordens_ativas: [
    { id:'1', numero:'OS-002184', ativo:'PR-AZT', tipo:'Inspeção 100h', categoria:'mecanica', responsavel:'Marcos Lima', status:'em_andamento', custo_estimado:28400, prazo:'2026-09-18T12:00:00Z' },
    { id:'2', numero:'OS-002179', ativo:'PT-FOX', tipo:'Revisão de aviônicos', categoria:'avionicos', responsavel:'Carla Mendes', status:'aguardando_pecas', custo_estimado:18750, prazo:'2026-09-17T18:00:00Z' },
    { id:'3', numero:'OS-002176', ativo:'PS-MTR', tipo:'Manutenção preventiva', categoria:'motor', responsavel:'Rafael Souza', status:'em_andamento', custo_estimado:42200, prazo:'2026-09-22T15:00:00Z' },
    { id:'4', numero:'OS-002171', ativo:'PR-JET', tipo:'Reparo estrutural', categoria:'estrutura', responsavel:'Ana Costa', status:'aberta', custo_estimado:12800, prazo:'2026-09-25T10:00:00Z' },
    { id:'5', numero:'OS-002168', ativo:'PP-ALX', tipo:'Troca de componentes', categoria:'mecanica', responsavel:'Diego Alves', status:'em_andamento', custo_estimado:9650, prazo:'2026-09-20T17:00:00Z' },
  ],
  distribuicao_categoria: [
    { categoria:'avionicos', quantidade:7, percentual:25 }, { categoria:'mecanica', quantidade:10, percentual:36 },
    { categoria:'estrutura', quantidade:5, percentual:18 }, { categoria:'motor', quantidade:6, percentual:21 },
  ],
  composicao_custos: { pecas: 118450.8, mao_de_obra: 65800, total: 184250.8 },
}
