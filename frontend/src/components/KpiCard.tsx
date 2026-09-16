import type { LucideIcon } from 'lucide-react'

interface Props { label: string; value: string; change?: number; note: string; icon: LucideIcon; tone?: 'default' | 'danger' | 'warning' }

export function KpiCard({ label, value, change, note, icon: Icon, tone = 'default' }: Props) {
  const accent = tone === 'danger' ? 'bg-red-50 text-danger' : tone === 'warning' ? 'bg-amber-50 text-amber-600' : 'bg-[#eef3f0] text-brand'
  return <article className="card min-w-0 p-5">
    <div className="mb-5 flex items-start justify-between gap-3"><p className="text-[12px] font-medium leading-5 text-muted">{label}</p><span className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg ${accent}`}><Icon size={16}/></span></div>
    <div className="flex items-end justify-between gap-2"><strong className={`truncate text-[25px] font-semibold tracking-[-.04em] ${tone === 'danger' ? 'text-danger' : ''}`}>{value}</strong>{change !== undefined && <span className={`mb-1 rounded-md px-2 py-1 text-[10px] font-bold ${change >= 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-danger'}`}>{change >= 0 ? '↑' : '↓'} {Math.abs(change)}%</span>}</div>
    <p className="mt-2 text-[10px] text-muted">{note}</p>
  </article>
}
