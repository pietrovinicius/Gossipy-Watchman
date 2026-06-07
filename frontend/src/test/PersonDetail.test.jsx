import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'

vi.mock('../services/api', () => ({
  default: { get: vi.fn(), patch: vi.fn() },
}))

vi.mock('../hooks/useAuthImage', () => ({
  useAuthImage: (filename) => (filename ? `blob:${filename}` : null),
}))

vi.mock('../utils/downloadCsv', () => ({
  downloadCsv: vi.fn(),
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

const MOCK_PERSON = {
  id: 1,
  name: 'Fulano',
  category: 'Visitante',
  notes: '',
  profile_image_path: null,
}

const MOCK_TIMELINE = [
  {
    id: 10,
    person_id: 1,
    video_id: 42,
    timestamp_start: 1.0,
    timestamp_end: 5.0,
    confidence: 0.45,
    file_name: 'reuniao.mp4',
  },
]

const MOCK_STATS = {
  video_count: 1,
  total_appearances: 1,
  total_seconds: 4.0,
  first_seen: '2026-06-01T10:00:00Z',
  last_seen: '2026-06-01T10:05:00Z',
}

async function renderPersonDetail() {
  const { default: PersonDetail } = await import('../pages/PersonDetail.jsx')
  return render(
    <MemoryRouter initialEntries={['/people/1']}>
      <Routes>
        <Route path="/people/:id" element={<PersonDetail />} />
      </Routes>
    </MemoryRouter>
  )
}

describe('PersonDetail — navegação cruzada para vídeo', () => {
  beforeEach(async () => {
    vi.resetModules()
    vi.clearAllMocks()
    const api = (await import('../services/api')).default
    api.get.mockImplementation((url) => {
      if (url.includes('/timeline')) return Promise.resolve({ data: MOCK_TIMELINE })
      if (url.includes('/frames')) return Promise.resolve({ data: [] })
      if (url.includes('/stats')) return Promise.resolve({ data: MOCK_STATS })
      if (url.includes('/quality')) return Promise.resolve({ data: {} })
      return Promise.resolve({ data: MOCK_PERSON })
    })
  })

  it('nome do vídeo na timeline é um link clicável', async () => {
    await renderPersonDetail()

    await waitFor(() => screen.getByText('reuniao.mp4'))

    const link = screen.getByText('reuniao.mp4').closest('[role="button"], a, button')
    expect(link).toBeTruthy()
  })

  it('clicar no nome do vídeo navega para /videos/{video_id}', async () => {
    await renderPersonDetail()

    await waitFor(() => screen.getByText('reuniao.mp4'))

    fireEvent.click(screen.getByText('reuniao.mp4'))

    expect(mockNavigate).toHaveBeenCalledWith('/videos/42')
  })
})
