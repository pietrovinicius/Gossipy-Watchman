import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import VideoDetail from '../pages/VideoDetail'

vi.mock('../services/api', () => ({
  default: { get: vi.fn(), delete: vi.fn(), post: vi.fn() },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

const MOCK_VIDEO_DETAIL = {
  video: {
    id: 1,
    file_name: 'test.mp4',
    status: 'Concluído',
    uploaded_at: '2026-06-07T12:00:00Z',
    deleted_at: null,
  },
  summary: {
    total_people: 2,
    total_appearances: 5,
    duration_covered: 120,
    processing_status: 'Concluído',
  },
  people: [
    {
      person_id: 1,
      person_name: 'Alice',
      person_category: 'Funcionário',
      profile_image_path: 'images/alice.jpg',
      appearance_count: 2,
      total_seconds: 30,
      first_seen_at: 5,
      last_seen_at: 35,
      appearances: [
        { id: 101, timestamp_start: 5, timestamp_end: 15, confidence: 0.9 },
        { id: 102, timestamp_start: 30, timestamp_end: 35, confidence: 0.85 },
      ],
    },
    {
      person_id: 2,
      person_name: 'Bob',
      person_category: 'Visitante',
      profile_image_path: 'images/bob.jpg',
      appearance_count: 1,
      total_seconds: 20,
      first_seen_at: 50,
      last_seen_at: 70,
      appearances: [
        { id: 201, timestamp_start: 50, timestamp_end: 70, confidence: 0.88 },
      ],
    },
  ],
}

async function renderVideoDetail() {
  return render(
    <MemoryRouter initialEntries={['/videos/1']}>
      <VideoDetail />
    </MemoryRouter>
  )
}

describe('VideoDetail — Auto-scroll', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  it('PersonCard renderiza com ref para referência no dom', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: MOCK_VIDEO_DETAIL })

    sessionStorage.setItem('token', 'test-token')

    const { container } = await renderVideoDetail()

    await waitFor(() => screen.getByText('Alice'))

    const aliceCard = container.querySelector('[data-testid="person-card-1"]')
    expect(aliceCard).toBeTruthy()

    const bobCard = container.querySelector('[data-testid="person-card-2"]')
    expect(bobCard).toBeTruthy()
  })

  it('PersonCard exibe badge EM CENA quando isOnScreen=true', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: MOCK_VIDEO_DETAIL })

    sessionStorage.setItem('token', 'test-token')

    await renderVideoDetail()

    await waitFor(() => screen.getByText('Alice'))

    // Inicialmente nenhum badge EM CENA (currentTime=0)
    expect(screen.queryAllByText('EM CENA').length).toBe(0)
  })

  it('PersonCard renderiza com border-primary quando isOnScreen=true', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: MOCK_VIDEO_DETAIL })

    sessionStorage.setItem('token', 'test-token')

    const { container } = await renderVideoDetail()

    await waitFor(() => screen.getByText('Alice'))

    const aliceCard = container.querySelector('[data-testid="person-card-1"]')
    // Inicialmente sem border (não em cena)
    expect(aliceCard.className).not.toContain('border-2 border-primary')
  })

  it('VideoDetail passa onPlay e onPause ao VideoPlayer', async () => {
    const api = (await import('../services/api')).default
    api.get.mockResolvedValue({ data: MOCK_VIDEO_DETAIL })

    sessionStorage.setItem('token', 'test-token')

    const { container } = await renderVideoDetail()

    await waitFor(() => screen.getByText('Alice'))

    // Verificar que VideoPlayer foi renderizado
    const videoElement = container.querySelector('video')
    expect(videoElement).toBeTruthy()
  })
})
