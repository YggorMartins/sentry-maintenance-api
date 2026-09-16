import axios from 'axios'
import { mockDashboard } from '../data/mockDashboard'
import type { DashboardData } from '../types'

const apiBaseUrl = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '/api' : '')
const api = axios.create({ baseURL: apiBaseUrl, timeout: 8000 })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sentry_access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function getDashboard(inicio: Date, fim: Date): Promise<DashboardData> {
  if (import.meta.env.VITE_USE_MOCKS !== 'false') return mockDashboard
  const { data } = await api.get<DashboardData>('/dashboard/resumo', { params: { inicio: inicio.toISOString(), fim: fim.toISOString() } })
  return data
}

export default api
