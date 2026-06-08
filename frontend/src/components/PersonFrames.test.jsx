import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'

// Mock FIRST before any imports
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('../hooks/useAuthImage', () => ({
  useAuthImage: vi.fn((filename) => `http://localhost:8000/api/v1/faces/${filename}`),
}))

// THEN import component and api after mocks
import PersonFrames from './PersonFrames'
import api from '../services/api'

const mockFrames = [
  {
    filename: '1_sample_001.jpg',
    is_primary: false,
    url: 'http://localhost:8000/api/v1/faces/1_sample_001.jpg',
  },
  {
    filename: '1_sample_002.jpg',
    is_primary: true,
    url: 'http://localhost:8000/api/v1/faces/1_sample_002.jpg',
  },
]

describe('PersonFrames - Set Primary Photo', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: mockFrames })
    api.patch.mockResolvedValue({
      data: {
        id: 1,
        name: 'Teste',
        profile_image_path: '/storage/faces/1.jpg',
      },
    })
  })

  it('should render frames gallery', async () => {
    render(<PersonFrames personId={1} />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/people/1/frames')
    })

    await waitFor(() => {
      expect(screen.getByText('Principal')).toBeInTheDocument()
    })
  })

  it('RED: should set primary photo when button is clicked', async () => {
    render(<PersonFrames personId={1} />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/people/1/frames')
    })

    const setButtons = await screen.findAllByText('Definir como principal')
    fireEvent.click(setButtons[0])

    await waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith(
        '/people/1/primary-photo',
        { filename: mockFrames[0].filename }
      )
    })

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledTimes(2)
    })
  })

  it('RED: should show error on PATCH failure', async () => {
    api.patch.mockRejectedValueOnce({
      response: {
        data: { detail: 'Erro ao definir foto principal' },
      },
    })

    render(<PersonFrames personId={1} />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/people/1/frames')
    })

    const setButtons = await screen.findAllByText('Definir como principal')
    fireEvent.click(setButtons[0])

    await waitFor(() => {
      expect(screen.getByText(/Erro ao definir foto principal/)).toBeInTheDocument()
    })
  })

  it('RED: should disable button while setting', async () => {
    api.patch.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ data: {} }), 500))
    )

    render(<PersonFrames personId={1} />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/people/1/frames')
    })

    const setButtons = await screen.findAllByText('Definir como principal')
    fireEvent.click(setButtons[0])

    await waitFor(() => {
      expect(screen.getByText('Definindo…')).toBeInTheDocument()
    })

    const definingButton = screen.getByText('Definindo…').closest('button')
    expect(definingButton).toBeDisabled()
  })
})
