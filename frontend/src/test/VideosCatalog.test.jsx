import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '../contexts/ThemeContext'
import VideosCatalog from '../pages/VideosCatalog'
import api from '../services/api'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockCatalogResponse = {
  items: [
    {
      id: 1,
      file_name: 'video1.mp4',
      status: 'Concluído',
      uploaded_at: '2026-06-07T10:00:00Z',
      people_count: 3,
      people_previews: [
        { person_id: 1, person_name: 'Alice', profile_image_path: null },
        { person_id: 2, person_name: 'Bob', profile_image_path: null },
      ],
    },
  ],
  total: 1,
  page: 1,
  page_size: 12,
  total_pages: 1,
  has_next: false,
  has_prev: false,
}

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  )
}

describe('VideosCatalog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.get = vi.fn().mockResolvedValue({ data: mockCatalogResponse })
    api.post = vi.fn().mockResolvedValue({ data: {} })
    api.delete = vi.fn().mockResolvedValue({ data: {} })
  })

  it('renders catalog with title', async () => {
    renderWithProviders(<VideosCatalog />)
    const headings = screen.getAllByText('Vídeos')
    expect(headings.length).toBeGreaterThan(0)
  })

  it('displays grid of cards for each video', async () => {
    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      expect(screen.getByText('video1.mp4')).toBeInTheDocument()
    })
  })

  it('displays video status badge', async () => {
    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      expect(screen.getByText('Concluído')).toBeInTheDocument()
    })
  })

  it('calls API with search query after debounce', async () => {
    renderWithProviders(<VideosCatalog />)
    const searchInput = screen.getByPlaceholderText('Buscar por nome...')
    fireEvent.change(searchInput, { target: { value: 'birthday' } })

    await waitFor(
      () => {
        const calls = api.get.mock.calls
        expect(calls.some(call => call[0].includes('q=birthday'))).toBe(true)
      },
      { timeout: 600 }
    )
  })

  it('filters by status when dropdown changes', async () => {
    renderWithProviders(<VideosCatalog />)
    const statusSelect = screen.getByDisplayValue('Todos')
    fireEvent.change(statusSelect, { target: { value: 'Concluído' } })

    await waitFor(() => {
      const calls = api.get.mock.calls
      expect(calls.some(call => call[0].includes('status=Conclu%C3%ADdo'))).toBe(true)
    })
  })

  it('toggles layout between grid and list', () => {
    renderWithProviders(<VideosCatalog />)
    const gridBtn = screen.getByTitle('Layout grid')
    const listBtn = screen.getByTitle('Layout lista')

    fireEvent.click(listBtn)
    expect(localStorage.getItem('gw-videos-layout')).toBe('list')

    fireEvent.click(gridBtn)
    expect(localStorage.getItem('gw-videos-layout')).toBe('grid')
  })

  it('toggles include_deleted when eye icon clicked', async () => {
    renderWithProviders(<VideosCatalog />)
    const toggleBtn = screen.getByTitle('Mostrar excluídos')
    fireEvent.click(toggleBtn)

    await waitFor(() => {
      const calls = api.get.mock.calls
      expect(calls.some(call => call[0].includes('include_deleted=true'))).toBe(true)
    })
  })

  it('displays people count for video', async () => {
    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      expect(screen.getByText(/👤 3 pessoas/)).toBeInTheDocument()
    })
  })

  it('displays mini gallery with up to 4 avatars', async () => {
    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      const alice = screen.queryByTitle('Alice')
      const bob = screen.queryByTitle('Bob')
      expect(alice || bob).toBeTruthy()
    })
  })

  it('shows +N badge when more than 4 people', async () => {
    const response = {
      ...mockCatalogResponse,
      items: [{
        ...mockCatalogResponse.items[0],
        people_count: 7,
        people_previews: [
          { person_id: 1, person_name: 'A', profile_image_path: null },
          { person_id: 2, person_name: 'B', profile_image_path: null },
          { person_id: 3, person_name: 'C', profile_image_path: null },
          { person_id: 4, person_name: 'D', profile_image_path: null },
          { person_id: 5, person_name: 'E', profile_image_path: null },
        ],
      }],
    }
    api.get = vi.fn().mockResolvedValue({ data: response })

    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      expect(screen.getByText(/\+3/)).toBeInTheDocument()
    })
  })

  it('pagination controls work correctly', async () => {
    const response = {
      ...mockCatalogResponse,
      total_pages: 3,
      has_next: true,
    }
    api.get = vi.fn().mockResolvedValue({ data: response })

    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      expect(screen.getByText('Exibindo 1-1 de 1 vídeos')).toBeInTheDocument()
    })

    const nextBtn = screen.getByTitle('Próxima página')
    expect(nextBtn).not.toBeDisabled()
  })

  it('next button disabled on last page', async () => {
    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      const nextBtn = screen.getByTitle('Próxima página')
      expect(nextBtn).toBeDisabled()
    })
  })

  it('delete action opens confirm modal', async () => {
    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      const deleteBtn = screen.getAllByTitle('Excluir')[0]
      fireEvent.click(deleteBtn)
    })

    await waitFor(() => {
      expect(screen.getByText('Excluir vídeo?')).toBeInTheDocument()
    })
  })

  it('export CSV triggers download', async () => {
    const mockBlob = new Blob(['mock csv'])
    api.get = vi.fn().mockImplementation((url) => {
      if (url.includes('/export/')) {
        return Promise.resolve({ data: mockBlob })
      }
      return Promise.resolve({ data: mockCatalogResponse })
    })

    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      const exportBtn = screen.getAllByTitle('Exportar CSV')[0]
      fireEvent.click(exportBtn)
    })

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        expect.stringContaining('/export/timeline/video/'),
        expect.anything()
      )
    })
  })

  it('displays empty state when no videos found', async () => {
    api.get = vi.fn().mockResolvedValue({
      data: {
        items: [],
        total: 0,
        page: 1,
        page_size: 12,
        total_pages: 0,
        has_next: false,
        has_prev: false,
      },
    })

    renderWithProviders(<VideosCatalog />)
    await waitFor(() => {
      expect(screen.getByText('Nenhum vídeo encontrado')).toBeInTheDocument()
    })
  })
})
