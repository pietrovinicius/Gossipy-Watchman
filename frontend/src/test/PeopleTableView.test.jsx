import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('../hooks/useAuthImage', () => ({
  useAuthImage: () => null,
}))

vi.mock('../hooks/useFaceSearch', () => ({
  useFaceSearch: () => ({
    results: [],
    loading: false,
    error: null,
    queryTimeMs: null,
    search: vi.fn(),
    reset: vi.fn(),
  }),
}))

import api from '../services/api'
import People from '../pages/People'

const MOCK_PEOPLE = [
  { id: 1, name: 'Zara Silva', category: 'Visitante', created_at: '2026-01-01T00:00:00Z', profile_image_path: null, deleted_at: null },
  { id: 2, name: 'Ana Costa', category: 'Funcionário', created_at: '2026-02-01T00:00:00Z', profile_image_path: null, deleted_at: null },
  { id: 3, name: 'Bruno Melo', category: 'Monitorado', created_at: '2026-03-01T00:00:00Z', profile_image_path: null, deleted_at: null },
]

function renderPeople() {
  return render(<MemoryRouter><People /></MemoryRouter>)
}

describe('People — view toggle tabela', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (url.includes('/alerts')) return Promise.resolve({ data: { unseen: 0 } })
      return Promise.resolve({ data: MOCK_PEOPLE })
    })
  })

  it('exibe botão de toggle para visão de tabela', async () => {
    renderPeople()
    await waitFor(() => screen.getByText('Zara Silva'))
    expect(screen.getByRole('button', { name: /tabela/i })).toBeTruthy()
  })

  it('clicar em Tabela exibe os nomes em linhas de tabela', async () => {
    renderPeople()
    await waitFor(() => screen.getByText('Zara Silva'))

    fireEvent.click(screen.getByRole('button', { name: /tabela/i }))

    await waitFor(() => {
      // todos os nomes visíveis na tabela
      expect(screen.getAllByText('Zara Silva').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Ana Costa').length).toBeGreaterThan(0)
    })
  })

  it('tabela exibe pessoas ordenadas por nome (A→Z) por padrão', async () => {
    renderPeople()
    await waitFor(() => screen.getByText('Zara Silva'))

    fireEvent.click(screen.getByRole('button', { name: /tabela/i }))

    await waitFor(() => screen.getAllByRole('row'))

    const rows = screen.getAllByRole('row')
    // primeira linha de dado (índice 1 pois 0 é o header)
    expect(rows[1].textContent).toMatch(/Ana Costa/)
    expect(rows[2].textContent).toMatch(/Bruno Melo/)
    expect(rows[3].textContent).toMatch(/Zara Silva/)
  })

  it('clicar no cabeçalho Nome inverte ordem para Z→A', async () => {
    renderPeople()
    await waitFor(() => screen.getByText('Zara Silva'))

    fireEvent.click(screen.getByRole('button', { name: /tabela/i }))
    await waitFor(() => screen.getAllByRole('row'))

    // clica no header Nome para inverter
    fireEvent.click(screen.getByTestId('sort-by-name'))
    await waitFor(() => screen.getAllByRole('row'))

    const rows = screen.getAllByRole('row')
    expect(rows[1].textContent).toMatch(/Zara Silva/)
    expect(rows[3].textContent).toMatch(/Ana Costa/)
  })
})
