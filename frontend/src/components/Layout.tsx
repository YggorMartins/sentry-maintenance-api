import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function Layout() {
  const [menuOpen, setMenuOpen] = useState(false)
  return <div className="min-h-screen"><Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} /><Header onMenu={() => setMenuOpen(true)} /><main className="lg:ml-[252px]"><Outlet /></main></div>
}
