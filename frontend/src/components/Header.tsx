import { Bell, ChevronDown, Menu, Search } from 'lucide-react'

export function Header({ onMenu }: { onMenu: () => void }) {
  return <header className="sticky top-0 z-20 flex h-[76px] items-center justify-between border-b bg-white/95 px-4 backdrop-blur md:px-7 lg:ml-[252px]">
    <div className="flex min-w-0 flex-1 items-center gap-3">
      <button onClick={onMenu} className="rounded-lg p-2 hover:bg-canvas lg:hidden" aria-label="Abrir menu"><Menu size={21}/></button>
      <label className="flex h-10 w-full max-w-[440px] items-center gap-2.5 rounded-xl border bg-canvas/70 px-3.5 text-muted focus-within:border-brand/30 focus-within:ring-2 focus-within:ring-brand/10">
        <Search size={17}/><input className="min-w-0 flex-1 bg-transparent text-[13px] outline-none placeholder:text-muted/75" placeholder="Pesquisar aeronaves, tarefas, peças..." />
        <kbd className="hidden rounded border bg-white px-1.5 py-0.5 text-[10px] sm:inline">⌘ K</kbd>
      </label>
    </div>
    <div className="ml-4 flex items-center gap-3">
      <div className="hidden items-center gap-2 rounded-full border px-3 py-1.5 text-[11px] font-semibold text-brand md:flex"><span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_0_3px_rgba(16,185,129,.12)]"/>Sistemas operacionais</div>
      <button className="relative rounded-xl border p-2.5 text-muted hover:bg-canvas"><Bell size={17}/><span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-danger"/></button>
      <button className="flex items-center gap-2 border-l pl-3">
        <span className="grid h-9 w-9 place-items-center rounded-full bg-[#dfe8e3] text-xs font-bold text-brand">RM</span>
        <span className="hidden text-left md:block"><span className="block text-xs font-semibold">Ricardo Moura</span><span className="block text-[10px] text-muted">Gestor de manutenção</span></span>
        <ChevronDown size={14} className="hidden text-muted md:block"/>
      </button>
    </div>
  </header>
}
