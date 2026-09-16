import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, Boxes, CalendarDays, ChevronDown, CircleDollarSign, ClipboardCheck, MoreHorizontal, Plane, TrendingUp } from 'lucide-react'
import { KpiCard } from '../components/KpiCard'
import { StatusBadge } from '../components/StatusBadge'
import { getDashboard } from '../services/api'
import type { Categoria, DashboardData } from '../types'

const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
const categoryLabel: Record<Categoria, string> = { avionicos:'Elétrica / Aviônicos', mecanica:'Serviços mecânicos', estrutura:'Pneus / Estrutura', motor:'Motor' }
const colors: Record<Categoria, string> = { avionicos:'#235c49', mecanica:'#92ae31', estrutura:'#d5a83e', motor:'#cb6b5c' }

function monthRange() { const now = new Date(); return { start: new Date(now.getFullYear(), now.getMonth(), 1), end: new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59) } }

export function Dashboard() {
  const [period, setPeriod] = useState<'month'|'quarter'>('month')
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const range = useMemo(() => { const r = monthRange(); if (period === 'quarter') r.start.setMonth(r.start.getMonth() - 2); return r }, [period])
  useEffect(() => { setLoading(true); getDashboard(range.start, range.end).then(setData).catch(() => setError(true)).finally(() => setLoading(false)) }, [range])

  if (loading) return <div className="p-7"><div className="h-8 w-52 animate-pulse rounded bg-line"/><div className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-4">{[1,2,3,4].map(i=><div key={i} className="h-40 animate-pulse rounded-[18px] bg-white"/>)}</div></div>
  if (error || !data) return <div className="p-8"><div className="card p-8 text-center"><AlertTriangle className="mx-auto mb-3 text-danger"/><h2 className="font-semibold">Não foi possível carregar o painel</h2><p className="mt-1 text-sm text-muted">Verifique a conexão com a API e tente novamente.</p></div></div>

  const { kpis } = data
  const parts = data.distribuicao_categoria.map(x => `${colors[x.categoria]} 0 ${x.percentual}%`)
  let cursor = 0
  const gradient = data.distribuicao_categoria.map(x => { const start=cursor; cursor += x.percentual; return `${colors[x.categoria]} ${start}% ${cursor}%` }).join(',')
  const pecasPct = data.composicao_custos.total ? data.composicao_custos.pecas / data.composicao_custos.total * 100 : 0

  return <div className="mx-auto max-w-[1600px] p-4 sm:p-6 xl:p-7">
    <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div><p className="mb-1 text-[11px] font-semibold uppercase tracking-[.13em] text-brand">Operações</p><h1 className="text-[25px] font-semibold tracking-[-.035em]">Dashboard de manutenção</h1><p className="mt-1 text-xs text-muted">Visão consolidada da operação, custos e disponibilidade da frota.</p></div>
      <div className="flex items-center gap-2">
        <div className="flex rounded-xl border bg-white p-1 text-[11px] font-semibold"><button onClick={()=>setPeriod('month')} className={`rounded-lg px-3 py-2 ${period==='month'?'bg-ink text-white':'text-muted'}`}>Este mês</button><button onClick={()=>setPeriod('quarter')} className={`rounded-lg px-3 py-2 ${period==='quarter'?'bg-ink text-white':'text-muted'}`}>Trimestre</button></div>
        <button className="flex items-center gap-2 rounded-xl border bg-white px-3 py-2.5 text-[11px] font-semibold text-muted"><CalendarDays size={14}/> Datas <ChevronDown size={13}/></button>
      </div>
    </div>

    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="Custo total de manutenção" value={brl.format(kpis.custo_total)} change={kpis.variacao_custo_percentual} note="comparado ao período anterior" icon={CircleDollarSign}/>
      <KpiCard label="Manutenções ativas" value={String(kpis.manutencoes_ativas).padStart(2,'0')} change={kpis.variacao_ativas_percentual} note="ordens de serviço em andamento" icon={ClipboardCheck}/>
      <KpiCard label="Tarefas críticas / atrasadas" value={String(kpis.tarefas_criticas).padStart(2,'0')} note="requerem atenção imediata" icon={AlertTriangle} tone="danger"/>
      <KpiCard label="Alertas de estoque" value={String(kpis.alertas_estoque).padStart(2,'0')} note="peças abaixo do nível mínimo" icon={Boxes} tone="warning"/>
    </section>

    <section className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.9fr)_minmax(300px,.8fr)]">
      <div className="card min-w-0 overflow-hidden">
        <div className="flex items-center justify-between border-b px-5 py-4"><div><h2 className="text-sm font-semibold">Ordens de serviço ativas</h2><p className="mt-1 text-[10px] text-muted">Acompanhamento das manutenções em execução</p></div><button className="text-[11px] font-semibold text-brand">Ver todas →</button></div>
        <div className="overflow-x-auto"><table className="w-full min-w-[820px] text-left">
          <thead><tr className="bg-[#fafbfa] text-[9px] font-bold uppercase tracking-[.09em] text-muted"><th className="px-5 py-3">Código O.S.</th><th className="px-3 py-3">Ativo / Aeronave</th><th className="px-3 py-3">Tipo de manutenção</th><th className="px-3 py-3">Responsável técnico</th><th className="px-3 py-3">Status</th><th className="px-3 py-3 text-right">Custo estimado</th><th/></tr></thead>
          <tbody className="divide-y">{data.ordens_ativas.map(os => <tr key={os.id} className="group text-[11px] hover:bg-canvas/60"><td className="px-5 py-4 font-semibold text-brand">{os.numero}</td><td className="px-3 py-4"><span className="flex items-center gap-2 font-semibold"><span className="grid h-7 w-7 place-items-center rounded-lg bg-canvas text-muted"><Plane size={13}/></span>{os.ativo}</span></td><td className="px-3 py-4 text-muted">{os.tipo.replaceAll('_',' ')}</td><td className="px-3 py-4 text-muted">{os.responsavel || 'Não atribuído'}</td><td className="px-3 py-4"><StatusBadge status={os.status}/></td><td className="px-3 py-4 text-right font-semibold">{brl.format(os.custo_estimado)}</td><td className="pr-4 text-right"><button className="rounded p-1 text-muted opacity-50 hover:bg-line group-hover:opacity-100"><MoreHorizontal size={15}/></button></td></tr>)}</tbody>
        </table></div>
        <div className="flex items-center justify-between border-t px-5 py-3 text-[10px] text-muted"><span>Exibindo {data.ordens_ativas.length} ordens prioritárias</span><span>Atualizado agora</span></div>
      </div>

      <aside className="space-y-5">
        <div className="card p-5"><div className="mb-5 flex items-start justify-between"><div><h2 className="text-sm font-semibold">Distribuição por categoria</h2><p className="mt-1 text-[10px] text-muted">Manutenções ativas</p></div><button className="text-muted"><MoreHorizontal size={17}/></button></div>
          <div className="flex items-center gap-7"><div className="relative h-[118px] w-[118px] shrink-0 rounded-full" style={{background:`conic-gradient(${gradient || parts.join(',')})`}}><div className="absolute inset-[15px] grid place-items-center rounded-full bg-white text-center"><span><b className="block text-xl">{kpis.manutencoes_ativas}</b><span className="text-[9px] text-muted">total</span></span></div></div><div className="min-w-0 flex-1 space-y-3">{data.distribuicao_categoria.map(x=><div key={x.categoria} className="flex items-center justify-between gap-3 text-[10px]"><span className="flex min-w-0 items-center gap-2 text-muted"><i className="h-2 w-2 shrink-0 rounded-full" style={{background:colors[x.categoria]}}/><span className="truncate">{categoryLabel[x.categoria]}</span></span><b>{x.percentual}%</b></div>)}</div></div>
        </div>
        <div className="card p-5"><div className="mb-5 flex items-start justify-between"><div><h2 className="text-sm font-semibold">Composição de custos</h2><p className="mt-1 text-[10px] text-muted">Peças vs. mão de obra</p></div><span className="grid h-8 w-8 place-items-center rounded-lg bg-emerald-50 text-brand"><TrendingUp size={15}/></span></div>
          <div className="mb-4 flex h-2 overflow-hidden rounded-full bg-line"><span className="bg-brand" style={{width:`${pecasPct}%`}}/><span className="bg-lime" style={{width:`${100-pecasPct}%`}}/></div>
          <div className="grid grid-cols-2 gap-3"><div className="rounded-xl bg-canvas p-3"><span className="mb-2 flex items-center gap-2 text-[9px] text-muted"><i className="h-2 w-2 rounded-full bg-brand"/>Peças</span><b className="text-[13px]">{brl.format(data.composicao_custos.pecas)}</b><span className="mt-1 block text-[9px] text-muted">{pecasPct.toFixed(0)}% do total</span></div><div className="rounded-xl bg-canvas p-3"><span className="mb-2 flex items-center gap-2 text-[9px] text-muted"><i className="h-2 w-2 rounded-full bg-lime"/>Mão de obra</span><b className="text-[13px]">{brl.format(data.composicao_custos.mao_de_obra)}</b><span className="mt-1 block text-[9px] text-muted">{(100-pecasPct).toFixed(0)}% do total</span></div></div>
        </div>
      </aside>
    </section>
  </div>
}
