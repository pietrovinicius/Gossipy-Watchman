import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../services/api', () => ({
  default: { get: vi.fn(), patch: vi.fn() },
}))

import api from '../services/api'
import PersonFrames from '../components/PersonFrames.jsx'

vi.mock('../hooks/useAuthImage', () => ({
  useAuthImage: (filename) => (filename ? `blob:${filename}` : null),
}))

const FRAMES = [
  { filename: '3.jpg', is_primary: true, url: '/api/v1/faces/3.jpg' },
  { filename: '3_sample_5.jpg', is_primary: false, url: '/api/v1/faces/3_sample_5.jpg' },
]

describe('PersonFrames', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exibe estado de carregamento inicialmente', () => {
    api.get.mockReturnValue(new Promise(() => {}))
    const { container } = render(<PersonFrames personId={3} />)
    expect(container.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('busca GET /people/{id}/frames e renderiza miniaturas', async () => {
    api.get.mockResolvedValue({ data: FRAMES })
    render(<PersonFrames personId={3} />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/people/3/frames')
    })
    await waitFor(() => {
      expect(screen.getAllByRole('img')).toHaveLength(2)
    })
  })

  it('exibe estado vazio quando não há frames', async () => {
    api.get.mockResolvedValue({ data: [] })
    render(<PersonFrames personId={3} />)

    await waitFor(() => {
      expect(screen.getByText(/nenhum frame/i)).toBeTruthy()
    })
  })

  it('exibe selo "Principal" no frame marcado como principal', async () => {
    api.get.mockResolvedValue({ data: FRAMES })
    render(<PersonFrames personId={3} />)

    await waitFor(() => {
      expect(screen.getByText('Principal')).toBeTruthy()
    })
  })

  it('botão "Definir como principal" chama PATCH com filename correto', async () => {
    api.get.mockResolvedValue({ data: FRAMES })
    api.patch.mockResolvedValue({ data: { id: 3, profile_image_path: '/x/3.jpg' } })
    render(<PersonFrames personId={3} />)

    const btn = await screen.findByRole('button', { name: /definir como principal/i })
    fireEvent.click(btn)

    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith('/people/3/primary-photo', { filename: '3_sample_5.jpg' })
    })
  })

  it('refaz a busca após definir nova foto principal com sucesso', async () => {
    api.get.mockResolvedValue({ data: FRAMES })
    api.patch.mockResolvedValue({ data: { id: 3, profile_image_path: '/x/3_sample_5.jpg' } })
    render(<PersonFrames personId={3} />)

    const btn = await screen.findByRole('button', { name: /definir como principal/i })
    fireEvent.click(btn)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(2)
    })
  })

  it('exibe mensagem de erro quando PATCH falha', async () => {
    api.get.mockResolvedValue({ data: FRAMES })
    api.patch.mockRejectedValue(new Error('falhou'))
    render(<PersonFrames personId={3} />)

    const btn = await screen.findByRole('button', { name: /definir como principal/i })
    fireEvent.click(btn)

    await waitFor(() => {
      expect(screen.getByText(/erro ao definir/i)).toBeTruthy()
    })
  })
})
