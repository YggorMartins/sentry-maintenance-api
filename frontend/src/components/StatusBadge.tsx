import type { StatusOS } from '../types'

const labels: Record<StatusOS, string> = { aberta:'Aberta', em_andamento:'Em andamento', aguardando_pecas:'Aguardando peças', concluida:'Concluída', cancelada:'Cancelada' }
const styles: Record<StatusOS, string> = { aberta:'bg-sky-50 text-sky-700', em_andamento:'bg-emerald-50 text-emerald-700', aguardando_pecas:'bg-amber-50 text-amber-700', concluida:'bg-slate-100 text-slate-600', cancelada:'bg-red-50 text-red-700' }

export function StatusBadge({ status }: { status: StatusOS }) { return <span className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-[10px] font-semibold ${styles[status]}`}>{labels[status]}</span> }
