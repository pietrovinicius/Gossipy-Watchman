import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '../services/api'
import { useAuthVideoThumbnail } from '../hooks/useAuthVideoThumbnail'

const FAKE_OBJECT_URL = 'blob:http://localhost/fake-uuid'

beforeEach(() => {
  vi.clearAllMocks()
  globalThis.URL.createObjectURL = vi.fn(() => FAKE_OBJECT_URL)
  globalThis.URL.revokeObjectURL = vi.fn()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('useAuthVideoThumbnail', () => {
  it('retorna null enquanto carregando', () => {
    api.get.mockReturnValue(new Promise(() => {}))
    const { result } = renderHook(() => useAuthVideoThumbnail(1, true))
    expect(result.current).toBeNull()
  })

  it('chama api.get com path correto quando vídeo tem thumbnail', async () => {
    api.get.mockResolvedValue({ data: new Blob(['img'], { type: 'image/jpeg' }) })
    renderHook(() => useAuthVideoThumbnail(1, true))
    await act(async () => {})
    expect(api.get).toHaveBeenCalledWith('/videos/1/thumbnail', { responseType: 'blob' })
  })

  it('retorna object URL após resposta bem-sucedida', async () => {
    const blob = new Blob(['img'], { type: 'image/jpeg' })
    api.get.mockResolvedValue({ data: blob })
    const { result } = renderHook(() => useAuthVideoThumbnail(1, true))
    await act(async () => {})
    expect(result.current).toBe(FAKE_OBJECT_URL)
    expect(URL.createObjectURL).toHaveBeenCalledWith(blob)
  })

  it('retorna null em caso de erro (404, 401)', async () => {
    api.get.mockRejectedValue(new Error('401 Unauthorized'))
    const { result } = renderHook(() => useAuthVideoThumbnail(1, true))
    await act(async () => {})
    expect(result.current).toBeNull()
  })

  it('não chama api.get quando vídeo não tem thumbnail', () => {
    api.get.mockResolvedValue({ data: new Blob() })
    renderHook(() => useAuthVideoThumbnail(1, false))
    expect(api.get).not.toHaveBeenCalled()
  })

  it('não chama api.get quando videoId é null', () => {
    api.get.mockResolvedValue({ data: new Blob() })
    renderHook(() => useAuthVideoThumbnail(null, true))
    expect(api.get).not.toHaveBeenCalled()
  })
})
