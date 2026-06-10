import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

// Mock api module
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
  BACKEND_URL: 'http://localhost:8000',
}))

// Mock useGlobalWebSocket
vi.mock('../hooks/useGlobalWebSocket.js', () => ({
  useGlobalWebSocket: vi.fn(() => ({})),
}))

const MOCK_ALERTS = [
  {
    id: 1, person_id: 10, person_name: 'Suspeito A', video_id: 3,
    video_file_name: 'video.mp4', timestamp_in_video: 12.5,
    message: 'Pessoa monitorada detectada: Suspeito A', seen: false,
    created_at: '2026-06-06T10:00:00Z',
  },
  {
    id: 2, person_id: 11, person_name: 'Suspeito B', video_id: 3,
    video_file_name: 'video.mp4', timestamp_in_video: 20.0,
    message: 'Pessoa monitorada detectada: Suspeito B', seen: true,
    created_at: '2026-06-06T09:00:00Z',
  },
]

async function renderAlerts() {
  const { default: Alerts } = await import('../pages/Alerts.jsx')
  return render(
    <MemoryRouter>
      <Alerts />
    </MemoryRouter>
  )
}

describe('Alerts page', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('exibe lista de alertas carregada da API', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: MOCK_ALERTS })

    await renderAlerts()

    await waitFor(() => {
      expect(screen.getByText('Suspeito A')).toBeTruthy()
    })
    expect(screen.getByText('Suspeito B')).toBeTruthy()
  })

  it('exibe estado de loading antes dos dados chegarem', async () => {
    const api = (await import('../services/api')).default
    api.get.mockReturnValue(new Promise(() => {}))  // never resolves

    await renderAlerts()

    expect(screen.getByRole('status')).toBeTruthy()
  })

  it('exibe mensagem de lista vazia quando não há alertas', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: [] })

    await renderAlerts()

    await waitFor(() => {
      expect(screen.getByText(/no alerts/i)).toBeTruthy()
    })
  })

  it('chama PATCH /alerts/seen ao marcar como visto', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: MOCK_ALERTS })
    api.patch.mockResolvedValue({ data: { updated: 1 } })

    await renderAlerts()

    await waitFor(() => screen.getByText('Suspeito A'))

    const btn = screen.getAllByRole('button', { name: /mark as seen/i })[0]
    fireEvent.click(btn)

    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith(
        '/alerts/seen',
        expect.objectContaining({ alert_ids: expect.any(Array) })
      )
    })
  })

  it('diferencia alertas vistos de não vistos visualmente', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: MOCK_ALERTS })

    const { container } = await renderAlerts()

    await waitFor(() => screen.getByText('Suspeito A'))

    // unseen alert should have a visual indicator
    const unseenBadge = container.querySelector('[data-seen="false"]')
    const seenBadge = container.querySelector('[data-seen="true"]')
    expect(unseenBadge).toBeTruthy()
    expect(seenBadge).toBeTruthy()
  })
})
