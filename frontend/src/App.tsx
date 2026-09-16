import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Placeholder } from './pages/Placeholder'

export default function App() { return <Routes><Route element={<Layout/>}><Route index element={<Navigate to="/dashboard" replace/>}/><Route path="dashboard" element={<Dashboard/>}/><Route path="*" element={<Placeholder/>}/></Route></Routes> }
