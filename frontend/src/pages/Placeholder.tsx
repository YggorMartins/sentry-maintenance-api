import { Construction } from 'lucide-react'
import { useLocation } from 'react-router-dom'

export function Placeholder() { const location=useLocation(); return <div className="grid min-h-[calc(100vh-76px)] place-items-center p-8"><div className="card max-w-md p-10 text-center"><Construction className="mx-auto mb-4 text-brand"/><h1 className="text-xl font-semibold">Módulo preparado</h1><p className="mt-2 text-sm leading-6 text-muted">A rota <b>{location.pathname}</b> já está integrada ao shell do produto e pronta para receber o fluxo operacional.</p></div></div> }
