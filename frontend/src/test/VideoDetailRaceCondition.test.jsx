import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route, Link } from 'react-router-dom'
import VideoDetail from '../pages/VideoDetail'

vi.mock('../services/api', () => ({
  default: { get: vi.fn(), delete: vi.fn(), post: vi.fn() },
}))

vi.mock('../hooks/useAuthImage', () => ({
  useAuthImage: (filename) => (filename ? `blob:${filename}` : null),
}))

vi.mock('../utils/downloadCsv', () => ({
  downloadCsv: vi.fn(),
}))

function makeDetail(videoId, personName) {
  return {
    video: {
      id: videoId,
      file_name: `video-${videoId}.mp4`,
      file_path: `storage/videos/${videoId}.mp4`,
      status: 'Concluído',
      uploaded_at: '2026-06-07T12:00:00Z',
    },
    people: [
      {
        person_id: videoId * 100,
        person_name: personName,
        person_category: 'Visitante',
        profile_image_path: null,
        total_seconds: 5.0,
        appearance_count: 1,
        first_seen_at: 1.0,
        last_seen_at: 4.0,
        appearances: [{ id: 1, timestamp_start: 1.0, timestamp_end: 4.0, confidence: 0.3 }],
      },
    ],
    summary: {
      total_people: 1,
      total_appearances: 1,
      duration_covered: 3.0,
      processing_status: 'Concluído',
    },
  }
}

function Harness() {
  return (
    <MemoryRouter initialEntries={['/videos/1']}>
      <Link to="/videos/2">ir para vídeo 2</Link>
      <Routes>
        <Route path="/videos/:id" element={<VideoDetail />} />
      </Routes>
    </MemoryRouter>
  )
}

describe('VideoDetail — corrida entre respostas de vídeos diferentes', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    sessionStorage.setItem('token', 'test-token')
  })

  it('não exibe pessoas do vídeo anterior quando a resposta antiga chega depois da nova', async () => {
    const api = (await import('../services/api')).default

    let resolveVideo1
    const video1Promise = new Promise((resolve) => {
      resolveVideo1 = resolve
    })

    api.get.mockImplementation((url) => {
      if (url === '/videos/1/detail') return video1Promise
      if (url === '/videos/2/detail') return Promise.resolve({ data: makeDetail(2, 'Pessoa do Vídeo 2') })
      return Promise.resolve({ data: {} })
    })

    render(<Harness />)

    // Navega para o vídeo 2 antes da resposta do vídeo 1 chegar
    fireEvent.click(screen.getByText('ir para vídeo 2'))

    await waitFor(() => {
      expect(screen.getByText('Pessoa do Vídeo 2')).toBeInTheDocument()
    })

    // Resposta atrasada do vídeo 1 chega agora — não deve sobrescrever a tela do vídeo 2
    resolveVideo1({ data: makeDetail(1, 'Pessoa do Vídeo 1') })

    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(screen.queryByText('Pessoa do Vídeo 1')).not.toBeInTheDocument()
    expect(screen.getByText('Pessoa do Vídeo 2')).toBeInTheDocument()
  })
})
