import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('../hooks/useGlobalWebSocket', () => ({
  useGlobalWebSocket: vi.fn(() => ({})),
}))

vi.mock('../utils/downloadCsv', () => ({
  downloadCsv: vi.fn(),
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

const MOCK_VIDEOS = [
  { id: 5, file_name: 'video5.mp4', status: 'Concluído', uploaded_at: '2026-06-07T12:00:00Z' },
  { id: 6, file_name: 'video6.mp4', status: 'Pendente', uploaded_at: '2026-06-07T13:00:00Z' },
]

const MOCK_PEOPLE = [{ id: 1, name: 'Fulano' }]

async function renderDashboard() {
  const { default: Dashboard } = await import('../pages/Dashboard.jsx')
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>
  )
}

describe('Dashboard — vídeos clicáveis', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('clicar na linha do vídeo navega para /videos/{id}', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.startsWith('/videos')) return Promise.resolve({ data: MOCK_VIDEOS })
      return Promise.resolve({ data: MOCK_PEOPLE })
    })

    const { container } = await renderDashboard()

    await waitFor(() => screen.getByText('video5.mp4'))

    const row = container.querySelector('tbody tr')
    fireEvent.click(row)

    expect(mockNavigate).toHaveBeenCalledWith('/videos/5')
  })

  it('clicar no ícone de exportar NÃO navega (stopPropagation)', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.startsWith('/videos')) return Promise.resolve({ data: MOCK_VIDEOS })
      return Promise.resolve({ data: MOCK_PEOPLE })
    })

    await renderDashboard()

    await waitFor(() => screen.getByText('video5.mp4'))

    const exportBtn = screen.getAllByLabelText(/export csv of video/i)[0]
    fireEvent.click(exportBtn)

    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('linha da tabela tem cursor-pointer', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.startsWith('/videos')) return Promise.resolve({ data: MOCK_VIDEOS })
      return Promise.resolve({ data: MOCK_PEOPLE })
    })

    const { container } = await renderDashboard()

    await waitFor(() => screen.getByText('video5.mp4'))

    const row = container.querySelector('tbody tr')
    expect(row.className).toMatch(/cursor-pointer/)
  })

  it('renderiza ChevronRight em cada linha', async () => {
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.startsWith('/videos')) return Promise.resolve({ data: MOCK_VIDEOS })
      return Promise.resolve({ data: MOCK_PEOPLE })
    })

    const { container } = await renderDashboard()

    await waitFor(() => screen.getByText('video5.mp4'))

    const rows = container.querySelectorAll('tbody tr')
    expect(rows.length).toBe(2)
    rows.forEach((row) => {
      expect(row.querySelector('svg.lucide-chevron-right')).toBeTruthy()
    })
  })
})
