import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'

const PERSON_NAMED = {
  id: 5, name: 'Fulano da Silva', profile_image_path: null,
  created_at: '2026-01-01T00:00:00Z', category: 'Visitante', notes: null, deleted_at: null,
}

const PERSON_UNKNOWN = {
  ...PERSON_NAMED, name: 'Desconhecido #5',
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
import PersonDetail from '../pages/PersonDetail'

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/people/5']}>
      <Routes>
        <Route path="/people/:id" element={<PersonDetail />} />
      </Routes>
    </MemoryRouter>
  )
}

function defaultGetImpl(person) {
  return (url) => {
    if (url.includes('/timeline')) return Promise.resolve({ data: [] })
    if (url.includes('/frames')) return Promise.resolve({ data: [] })
    if (url.includes('/stats')) return Promise.resolve({ data: { video_count: 0, total_seconds: 0, first_seen: null, last_seen: null } })
    if (url.includes('/quality')) return Promise.resolve({ data: {} })
    if (url.includes('/people/5')) return Promise.resolve({ data: person })
    return Promise.resolve({ data: {} })
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockImplementation(defaultGetImpl(PERSON_NAMED))
})

describe('PersonDetail — ações de exclusão e restauração de nome', () => {
  it('exibe botão "Excluir perfil"', async () => {
    renderPage()
    expect(await screen.findByRole('button', { name: /delete profile/i })).toBeTruthy()
  })

  it('abre ConfirmModal com requireTyping="excluir" e chama DELETE somente após digitar a palavra', async () => {
    api.delete.mockResolvedValue({ data: { ...PERSON_NAMED, deleted_at: '2026-03-01T00:00:00Z' } })
    renderPage()

    fireEvent.click(await screen.findByRole('button', { name: /delete profile/i }))

    const dialog = await screen.findByRole('dialog')
    const confirmBtn = within(dialog).getByRole('button', { name: /confirm/i })
    expect(confirmBtn).toBeDisabled()

    const input = within(dialog).getByRole('textbox')
    fireEvent.change(input, { target: { value: 'delete' } })
    expect(confirmBtn).not.toBeDisabled()

    fireEvent.click(confirmBtn)
    await vi.waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/people/5')
    })
  })

  it('exibe botão "Restaurar nome" quando nome não começa com "Desconhecido"', async () => {
    renderPage()
    expect(await screen.findByRole('button', { name: /restore original name/i })).toBeTruthy()
  })

  it('NÃO exibe botão "Restaurar nome" quando nome já é "Desconhecido #N"', async () => {
    api.get.mockImplementation(defaultGetImpl(PERSON_UNKNOWN))
    renderPage()
    await screen.findByText('Desconhecido #5')
    expect(screen.queryByRole('button', { name: /restore original name/i })).toBeNull()
  })

  it('clicar em "Restaurar nome" chama POST /people/{id}/reset-name e atualiza exibição', async () => {
    api.post.mockResolvedValue({ data: PERSON_UNKNOWN })
    renderPage()

    fireEvent.click(await screen.findByRole('button', { name: /restore original name/i }))

    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/people/5/reset-name')
    })
    expect(await screen.findByText('Desconhecido #5')).toBeTruthy()
  })

  it('após DELETE bem-sucedido, navega para /people', async () => {
    api.delete.mockResolvedValue({ data: { ...PERSON_NAMED, deleted_at: '2026-03-01T00:00:00Z' } })
    render(
      <MemoryRouter initialEntries={['/people/5']}>
        <Routes>
          <Route path="/people/:id" element={<PersonDetail />} />
          <Route path="/people" element={<div>Página de Pessoas</div>} />
        </Routes>
      </MemoryRouter>
    )

    fireEvent.click(await screen.findByRole('button', { name: /delete profile/i }))
    const dialog = await screen.findByRole('dialog')
    const input = within(dialog).getByRole('textbox')
    fireEvent.change(input, { target: { value: 'delete' } })
    fireEvent.click(within(dialog).getByRole('button', { name: /confirm/i }))

    await vi.waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/people/5')
    })
    expect(await screen.findByText('Página de Pessoas')).toBeTruthy()
  })
})
