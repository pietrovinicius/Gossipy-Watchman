import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'

const FAKE_OBJECT_URL = 'blob:http://localhost/fake-uuid'

beforeEach(() => {
  vi.clearAllMocks()
  globalThis.URL.createObjectURL = vi.fn(() => FAKE_OBJECT_URL)
  globalThis.URL.revokeObjectURL = vi.fn()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('useAuthImage', () => {
  it('retorna null enquanto carregando', () => {
    api.get.mockReturnValue(new Promise(() => {}))
    const { result } = renderHook(() => useAuthImage('1.jpg'))
    expect(result.current).toBeNull()
  })

  it('chama api.get com path correto e inclui cache-bust parameter', async () => {
    api.get.mockResolvedValue({ data: new Blob(['img'], { type: 'image/jpeg' }) })
    const { result } = renderHook(() => useAuthImage('1.jpg'))
    await act(async () => {})
    expect(api.get).toHaveBeenCalledWith('/faces/1.jpg?t=', { responseType: 'blob' })
  })

  it('retorna object URL após resposta bem-sucedida', async () => {
    const blob = new Blob(['img'], { type: 'image/jpeg' })
    api.get.mockResolvedValue({ data: blob })
    const { result } = renderHook(() => useAuthImage('1.jpg'))
    await act(async () => {})
    expect(result.current).toBe(FAKE_OBJECT_URL)
    expect(URL.createObjectURL).toHaveBeenCalledWith(blob)
  })

  it('retorna null em caso de erro (404, 401)', async () => {
    api.get.mockRejectedValue(new Error('401 Unauthorized'))
    const { result } = renderHook(() => useAuthImage('1.jpg'))
    await act(async () => {})
    expect(result.current).toBeNull()
  })

  it('não chama api.get quando filename é null', () => {
    api.get.mockResolvedValue({ data: new Blob() })
    renderHook(() => useAuthImage(null))
    expect(api.get).not.toHaveBeenCalled()
  })

  it('revoga object URL ao desmontar', async () => {
    api.get.mockResolvedValue({ data: new Blob(['img'], { type: 'image/jpeg' }) })
    const { result, unmount } = renderHook(() => useAuthImage('1.jpg'))
    await act(async () => {})
    expect(result.current).toBe(FAKE_OBJECT_URL)
    unmount()
    expect(URL.revokeObjectURL).toHaveBeenCalledWith(FAKE_OBJECT_URL)
  })
})
