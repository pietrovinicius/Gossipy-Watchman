import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

const PEOPLE = [
  { id: 1, name: 'Ativo', profile_image_path: null, created_at: '2026-01-01T00:00:00Z', category: 'Visitante', deleted_at: null },
  { id: 2, name: 'Removido', profile_image_path: null, created_at: '2026-01-02T00:00:00Z', category: 'Visitante', deleted_at: '2026-02-01T00:00:00Z' },
]

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
import People from '../pages/People'

beforeEach(() => {
  vi.clearAllMocks()
  api.get.mockImplementation((url) => {
    if (url.includes('include_deleted=true')) {
      return Promise.resolve({ data: PEOPLE })
    }
    return Promise.resolve({ data: PEOPLE.filter((p) => !p.deleted_at) })
  })
})

function renderPage() {
  return render(<MemoryRouter><People /></MemoryRouter>)
}

describe('People — exclusão e restauração', () => {
  it('exibe ícone de excluir em cada card de pessoa', async () => {
    renderPage()
    const deleteBtn = await screen.findByRole('button', { name: /delete ativo/i })
    expect(deleteBtn).toBeTruthy()
  })

  it('abre ConfirmModal ao clicar em excluir e chama DELETE ao confirmar', async () => {
    api.delete.mockResolvedValue({ data: { ...PEOPLE[0], deleted_at: '2026-03-01T00:00:00Z' } })
    renderPage()

    const deleteBtn = await screen.findByRole('button', { name: /delete ativo/i })
    fireEvent.click(deleteBtn)

    const dialog = await screen.findByRole('dialog')
    const confirmBtn = within(dialog).getByRole('button', { name: 'Delete' })
    fireEvent.click(confirmBtn)

    await vi.waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/people/1')
    })
  })

  it('toggle "Exibir excluídos" recarrega lista incluindo deletados', async () => {
    renderPage()
    await screen.findByRole('button', { name: /delete ativo/i })

    const toggle = screen.getByRole('button', { name: /show deleted/i })
    fireEvent.click(toggle)

    await vi.waitFor(() => {
      const calls = api.get.mock.calls.map((c) => c[0])
      expect(calls.some((url) => url.includes('include_deleted=true'))).toBe(true)
    })

    expect(await screen.findByText('Removido')).toBeTruthy()
  })

  it('exibe badge "Excluído" para pessoas com deleted_at preenchido', async () => {
    renderPage()
    await screen.findByRole('button', { name: /delete ativo/i })

    const toggle = screen.getByRole('button', { name: /show deleted/i })
    fireEvent.click(toggle)

    const removedName = await screen.findByText('Removido')
    const card = removedName.closest('.card')
    expect(within(card).getByText('Deleted')).toBeTruthy()
  })

  it('exibe botão de restaurar para pessoas deletadas e chama POST /restore', async () => {
    api.post.mockResolvedValue({ data: { ...PEOPLE[1], deleted_at: null } })
    renderPage()
    await screen.findByRole('button', { name: /delete ativo/i })

    const toggle = screen.getByRole('button', { name: /show deleted/i })
    fireEvent.click(toggle)
    await screen.findByText('Removido')

    const restoreBtn = screen.getByRole('button', { name: /restore removido/i })
    fireEvent.click(restoreBtn)

    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/people/2/restore')
    })
  })

  it('cards de pessoas deletadas têm opacidade reduzida', async () => {
    renderPage()
    await screen.findByRole('button', { name: /delete ativo/i })

    const toggle = screen.getByRole('button', { name: /show deleted/i })
    fireEvent.click(toggle)
    const removedName = await screen.findByText('Removido')

    const card = removedName.closest('.card')
    expect(card.className).toMatch(/opacity-50/)
  })

  it('cancelar no ConfirmModal não chama DELETE', async () => {
    renderPage()
    const deleteBtn = await screen.findByRole('button', { name: /delete ativo/i })
    fireEvent.click(deleteBtn)

    const dialog = await screen.findByRole('dialog')
    const cancelBtn = within(dialog).getByRole('button', { name: /cancelar/i })
    fireEvent.click(cancelBtn)

    expect(api.delete).not.toHaveBeenCalled()
  })
})
