import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

const VIDEOS = [
  { id: 1, file_name: 'ativo.mp4', status: 'Concluído', uploaded_at: '2026-01-01T00:00:00Z', deleted_at: null },
  { id: 2, file_name: 'removido.mp4', status: 'Erro', uploaded_at: '2026-01-02T00:00:00Z', deleted_at: '2026-02-01T00:00:00Z' },
]
const PEOPLE = []

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    post: vi.fn(),
  },
  BACKEND_URL: 'http://localhost:8000',
}))

vi.mock('../hooks/useGlobalWebSocket', () => ({
  useGlobalWebSocket: () => {},
}))

import api from '../services/api'
import Dashboard from '../pages/Dashboard'

beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockImplementation((url) => {
    if (url.startsWith('/people')) return Promise.resolve({ data: PEOPLE })
    if (url.includes('include_deleted=true')) return Promise.resolve({ data: VIDEOS })
    return Promise.resolve({ data: VIDEOS.filter((v) => !v.deleted_at) })
  })
})

function renderPage() {
  return render(<MemoryRouter><Dashboard /></MemoryRouter>)
}

describe('Dashboard — filtros, exclusão, restauração e reprocessamento', () => {
  it('exibe pills de filtro de status e refaz a busca com status selecionado', async () => {
    renderPage()
    await screen.findByText('ativo.mp4')

    const pill = screen.getByRole('button', { name: 'Error' })
    fireEvent.click(pill)

    await vi.waitFor(() => {
      const calls = api.get.mock.calls.map((c) => c[0])
      expect(calls.some((url) => url.includes('status=Erro'))).toBe(true)
    })
  })

  it('toggle "Mostrar excluídos" recarrega lista incluindo deletados', async () => {
    renderPage()
    await screen.findByText('ativo.mp4')

    const toggle = screen.getByRole('button', { name: /show deleted/i })
    fireEvent.click(toggle)

    await vi.waitFor(() => {
      const calls = api.get.mock.calls.map((c) => c[0])
      expect(calls.some((url) => url.includes('include_deleted=true'))).toBe(true)
    })
    expect(await screen.findByText('removido.mp4')).toBeTruthy()
  })

  it('abre ConfirmModal ao clicar em excluir vídeo e chama DELETE ao confirmar', async () => {
    api.delete.mockResolvedValue({ data: { ...VIDEOS[0], deleted_at: '2026-03-01T00:00:00Z' } })
    renderPage()
    await screen.findByText('ativo.mp4')

    const deleteBtn = screen.getByRole('button', { name: /delete video ativo\.mp4/i })
    fireEvent.click(deleteBtn)

    const dialog = await screen.findByRole('dialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Delete' }))

    await vi.waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/videos/1')
    })
  })

  it('exibe botão restaurar para vídeos deletados e chama POST /restore', async () => {
    api.post.mockResolvedValue({ data: { ...VIDEOS[1], deleted_at: null } })
    renderPage()
    await screen.findByText('ativo.mp4')

    fireEvent.click(screen.getByRole('button', { name: /show deleted/i }))
    await screen.findByText('removido.mp4')

    const restoreBtn = screen.getByRole('button', { name: /restore video removido\.mp4/i })
    fireEvent.click(restoreBtn)

    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/videos/2/restore')
    })
  })

  it('exibe botão reprocessar e chama POST /reprocess ao confirmar', async () => {
    api.post.mockResolvedValue({ data: { id: 1, status: 'Pendente' } })
    renderPage()
    await screen.findByText('ativo.mp4')

    const reprocessBtn = screen.getByRole('button', { name: /reprocess video ativo\.mp4/i })
    fireEvent.click(reprocessBtn)

    const dialog = await screen.findByRole('dialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Reprocess' }))

    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/videos/1/reprocess')
    })
  })
})
