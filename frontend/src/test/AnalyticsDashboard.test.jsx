import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
  },
  BACKEND_URL: 'http://localhost:8000',
}))

// Mock recharts to avoid SVG rendering complexity in jsdom
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
  LineChart: ({ children }) => <div data-testid="line-chart">{children}</div>,
  BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
  PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
  Line: () => null,
  Bar: () => null,
  Pie: () => null,
  Cell: () => null,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  Legend: () => null,
}))

const MOCK_OVERVIEW = { total_videos: 10, total_people: 25, total_appearances: 87 }
const MOCK_TIMELINE = [
  { date: '2026-06-01', count: 3 },
  { date: '2026-06-02', count: 5 },
]
const MOCK_TOP_PEOPLE = [
  { person_id: 1, person_name: 'Alice', appearance_count: 15 },
  { person_id: 2, person_name: 'Bob', appearance_count: 8 },
]
const MOCK_PER_VIDEO = [
  { video_id: 1, file_name: 'v1.mp4', count: 12 },
]

async function renderDashboard() {
  const { default: AnalyticsDashboard } = await import('../pages/AnalyticsDashboard.jsx')
  return render(
    <MemoryRouter>
      <AnalyticsDashboard />
    </MemoryRouter>
  )
}

describe('AnalyticsDashboard', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('exibe cards de métricas com total_videos, total_people, total_appearances', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.includes('overview')) return Promise.resolve({ data: MOCK_OVERVIEW })
      if (url.includes('timeline')) return Promise.resolve({ data: MOCK_TIMELINE })
      if (url.includes('top-people')) return Promise.resolve({ data: MOCK_TOP_PEOPLE })
      if (url.includes('per-video')) return Promise.resolve({ data: MOCK_PER_VIDEO })
      return Promise.resolve({ data: [] })
    })

    await renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('10')).toBeTruthy()
      expect(screen.getByText('25')).toBeTruthy()
      expect(screen.getByText('87')).toBeTruthy()
    })
  })

  it('exibe spinner enquanto carrega', async () => {
    const api = (await import('../services/api')).default
    api.get.mockReturnValue(new Promise(() => {}))

    await renderDashboard()

    expect(screen.getByRole('status')).toBeTruthy()
  })

  it('renderiza LineChart para timeline de atividade', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.includes('overview')) return Promise.resolve({ data: MOCK_OVERVIEW })
      if (url.includes('timeline')) return Promise.resolve({ data: MOCK_TIMELINE })
      if (url.includes('top-people')) return Promise.resolve({ data: MOCK_TOP_PEOPLE })
      if (url.includes('per-video')) return Promise.resolve({ data: MOCK_PER_VIDEO })
      return Promise.resolve({ data: [] })
    })

    const { container } = await renderDashboard()

    await waitFor(() => {
      expect(container.querySelector('[data-testid="line-chart"]')).toBeTruthy()
    })
  })

  it('renderiza BarChart para top pessoas', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.includes('overview')) return Promise.resolve({ data: MOCK_OVERVIEW })
      if (url.includes('timeline')) return Promise.resolve({ data: MOCK_TIMELINE })
      if (url.includes('top-people')) return Promise.resolve({ data: MOCK_TOP_PEOPLE })
      if (url.includes('per-video')) return Promise.resolve({ data: MOCK_PER_VIDEO })
      return Promise.resolve({ data: [] })
    })

    const { container } = await renderDashboard()

    await waitFor(() => {
      const barCharts = container.querySelectorAll('[data-testid="bar-chart"]')
      expect(barCharts.length).toBeGreaterThanOrEqual(1)
    })
  })

  it('exibe nomes de pessoas no ranking', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.includes('overview')) return Promise.resolve({ data: MOCK_OVERVIEW })
      if (url.includes('timeline')) return Promise.resolve({ data: MOCK_TIMELINE })
      if (url.includes('top-people')) return Promise.resolve({ data: MOCK_TOP_PEOPLE })
      if (url.includes('per-video')) return Promise.resolve({ data: MOCK_PER_VIDEO })
      return Promise.resolve({ data: [] })
    })

    await renderDashboard()

    await waitFor(() => {
      expect(screen.getByText(/Alice/)).toBeTruthy()
    })
  })

  it('exibe mensagem de erro se API falhar', async () => {
    const api = (await import('../services/api')).default
    api.get.mockRejectedValue(new Error('Falha de conexão'))

    await renderDashboard()

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeTruthy()
    })
  })
})
