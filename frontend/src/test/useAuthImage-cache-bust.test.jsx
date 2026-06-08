import { render, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mocka apenas api.get, não useAuthImage
vi.mock('../services/api')

import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'

describe('useAuthImage - cache bust parameter', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('inclui cache-bust parameter (t=cacheTag) na URL para evitar cache do browser', async () => {
    const mockBlob = new Blob(['fake image'])
    api.get.mockResolvedValue({ data: mockBlob })

    function TestComponent() {
      const src = useAuthImage('1.jpg', '123')
      return <img src={src} alt="test" />
    }

    render(<TestComponent />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/faces/1.jpg?t=123', expect.any(Object))
    })
  })

  it('atualiza cache-bust parameter quando cacheTag muda', async () => {
    const mockBlob = new Blob(['fake image'])
    api.get.mockResolvedValue({ data: mockBlob })

    let cacheTag = 'first'

    function TestComponent() {
      const src = useAuthImage('1.jpg', cacheTag)
      return <img src={src} alt="test" />
    }

    const { rerender } = render(<TestComponent />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/faces/1.jpg?t=first', expect.any(Object))
    })

    // Simula mudança de cacheTag
    cacheTag = 'second'
    rerender(<TestComponent />)

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/faces/1.jpg?t=second', expect.any(Object))
      expect(api.get).toHaveBeenCalledTimes(2)
    })
  })
})
