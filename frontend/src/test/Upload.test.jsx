import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Upload from '../pages/Upload'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { unseen: 0 } }),
    post: vi.fn(),
  },
}))

vi.mock('../hooks/useUploadProgress', () => ({
  useUploadProgress: () => ({
    progress: 0,
    speed: 0,
    loaded: 0,
    total: 0,
    eta: null,
    onUploadProgress: vi.fn(),
    reset: vi.fn(),
  }),
}))

import api from '../services/api'

function renderUpload() {
  return render(
    <MemoryRouter>
      <Upload />
    </MemoryRouter>
  )
}

function makeDavFile(name = 'video.dav') {
  return new File(['fake video content'], name, { type: 'video/x-dv' })
}

describe('Upload — upload multipart', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('envia FormData sem Content-Type manual (evita bug de boundary ausente)', async () => {
    api.post.mockResolvedValue({ data: { id: 1, status: 'Pendente' } })
    renderUpload()

    const input = document.querySelector('input[type="file"]')
    fireEvent.change(input, { target: { files: [makeDavFile()] } })

    const btn = screen.getByRole('button', { name: /send video/i })
    fireEvent.click(btn)

    await waitFor(() => expect(api.post).toHaveBeenCalled())

    const [, , config] = api.post.mock.calls[0]
    // Content-Type não deve ser definido manualmente — deixar o browser/axios setar com boundary
    expect(config?.headers?.['Content-Type']).toBeUndefined()
  })

  it('exibe detail do backend quando upload falha com 400', async () => {
    api.post.mockRejectedValue({
      message: 'Request failed with status code 400',
      response: { data: { detail: "Formato '' não suportado. Use .mp4 ou .avi." } },
    })
    renderUpload()

    const input = document.querySelector('input[type="file"]')
    fireEvent.change(input, { target: { files: [makeDavFile()] } })

    const btn = screen.getByRole('button', { name: /send video/i })
    fireEvent.click(btn)

    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent("Formato '' não suportado")
    )
  })

  it('reset() não lança ReferenceError ao remover arquivo selecionado', () => {
    renderUpload()

    const input = document.querySelector('input[type="file"]')
    fireEvent.change(input, { target: { files: [makeDavFile()] } })

    const removeBtn = screen.getByRole('button', { name: /remove file/i })
    expect(() => fireEvent.click(removeBtn)).not.toThrow()
  })
})
