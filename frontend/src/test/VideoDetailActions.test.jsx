import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'

const VIDEO_ACTIVE = {
  id: 7, file_name: 'reuniao.mp4', status: 'Concluído', uploaded_at: '2026-01-01T00:00:00Z', deleted_at: null,
}
const VIDEO_DELETED = { ...VIDEO_ACTIVE, deleted_at: '2026-02-01T00:00:00Z' }

const DETAIL = {
  video: VIDEO_ACTIVE,
  summary: { total_people: 0, total_appearances: 0, duration_covered: 0, processing_status: 'Concluído' },
  people: [],
}

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    post: vi.fn(),
  },
  BACKEND_URL: 'http://localhost:8000',
}))

import api from '../services/api'
import VideoDetail from '../pages/VideoDetail'

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/videos/7']}>
      <Routes>
        <Route path="/videos/:id" element={<VideoDetail />} />
      </Routes>
    </MemoryRouter>
  )
}

function mockDetail(video) {
  api.get.mockImplementation((url) => {
    if (url.includes('/detail')) return Promise.resolve({ data: { ...DETAIL, video } })
    return Promise.resolve({ data: {} })
  })
}

beforeEach(() => {
  vi.clearAllMocks()
  mockDetail(VIDEO_ACTIVE)
})

describe('VideoDetail — exclusão, restauração e reprocessamento', () => {
  it('exibe botão "Excluir vídeo" e chama DELETE somente após digitar "excluir"', async () => {
    api.delete.mockResolvedValue({ data: { ...VIDEO_ACTIVE, deleted_at: '2026-03-01T00:00:00Z' } })
    renderPage()

    fireEvent.click(await screen.findByRole('button', { name: /delete video/i }))

    const dialog = await screen.findByRole('dialog')
    const confirmBtn = within(dialog).getByRole('button', { name: /confirm/i })
    expect(confirmBtn).toBeDisabled()

    fireEvent.change(within(dialog).getByRole('textbox'), { target: { value: 'delete' } })
    expect(confirmBtn).not.toBeDisabled()
    fireEvent.click(confirmBtn)

    await vi.waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/videos/7')
    })
  })

  it('exibe botão "Reprocessar" e chama POST /reprocess ao confirmar', async () => {
    api.post.mockResolvedValue({ data: { id: 7, status: 'Pendente' } })
    renderPage()

    fireEvent.click(await screen.findByRole('button', { name: /reprocess/i }))

    const dialog = await screen.findByRole('dialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Reprocess' }))

    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/videos/7/reprocess')
    })
  })

  it('exibe botão "Restaurar vídeo" quando vídeo está deletado e chama POST /restore', async () => {
    mockDetail(VIDEO_DELETED)
    api.post.mockResolvedValue({ data: { ...VIDEO_DELETED, deleted_at: null } })
    renderPage()

    const restoreBtn = await screen.findByRole('button', { name: /restore video/i })
    fireEvent.click(restoreBtn)

    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/videos/7/restore')
    })
  })

  it('NÃO exibe botão "Excluir vídeo" quando vídeo já está deletado', async () => {
    mockDetail(VIDEO_DELETED)
    renderPage()

    await screen.findByRole('button', { name: /restore video/i })
    expect(screen.queryByRole('button', { name: /delete video/i })).toBeNull()
  })
})
