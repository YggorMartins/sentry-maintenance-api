import { BarChart3, Boxes, ChartNoAxesCombined, ClipboardList, Gauge, Plane, Settings2, ShieldCheck, UsersRound, Wrench } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const groups = [
  { label: 'GERAL', items: [
    ['Visão geral', '/', Gauge], ['Dashboard de manutenção', '/dashboard', BarChart3], ['Frota / Ativos', '/frota', Plane],
    ['Tarefas & Ordens de Serviço', '/ordens', ClipboardList], ['Mecânicos / Técnicos', '/tecnicos', UsersRound], ['Estoque de peças', '/estoque', Boxes],
  ]},
  { label: 'RELATÓRIOS', items: [
    ['Análise de custos', '/relatorios/custos', ChartNoAxesCombined], ['O.S. por categoria', '/relatorios/categorias', Wrench], ['Previsão de manutenção', '/relatorios/previsao', ShieldCheck],
  ]},
] as const

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  return <>
    {open && <button aria-label="Fechar menu" className="fixed inset-0 z-30 bg-black/25 lg:hidden" onClick={onClose} />}
    <aside className={`fixed inset-y-0 left-0 z-40 flex w-[252px] flex-col border-r bg-white transition-transform lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}>
      <div className="flex h-[76px] items-center gap-3 px-6">
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand text-white"><Plane size={19} strokeWidth={2.4} /></div>
        <div><div className="text-[15px] font-bold tracking-tight">Sentry</div><div className="text-[10px] font-semibold uppercase tracking-[.16em] text-muted">Maintenance</div></div>
      </div>
      <nav className="flex-1 space-y-7 overflow-y-auto px-3 py-5">
        {groups.map(group => <section key={group.label}>
          <p className="mb-2 px-3 text-[10px] font-bold tracking-[.16em] text-muted/70">{group.label}</p>
          <div className="space-y-1">{group.items.map(([label, href, Icon]) =>
            <NavLink key={href} to={href} end={href === '/'} onClick={onClose} className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition ${isActive ? 'bg-[#eef3f0] text-brand' : 'text-[#66716c] hover:bg-canvas hover:text-ink'}`}>
              <Icon size={17} strokeWidth={1.8} /><span>{label}</span>
            </NavLink>)}
          </div>
        </section>)}
      </nav>
      <div className="border-t p-4"><button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium text-muted hover:bg-canvas"><Settings2 size={17}/>Configurações</button></div>
    </aside>
  </>
}
