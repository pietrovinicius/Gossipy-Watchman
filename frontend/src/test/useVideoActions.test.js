import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useVideoActions } from '../hooks/useVideoActions'
import api from '../services/api'
import * as downloadModule from '../utils/downloadCsv'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('../utils/downloadCsv', () => ({
  downloadCsv: vi.fn(),
}))

describe('useVideoActions', () => {
  const mockOnSuccess = vi.fn()
  const mockOnError = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exportCsv calls GET /export/timeline/video/{id}', async () => {
    const mockBlob = new Blob(['data'])
    api.get.mockResolvedValue({ data: mockBlob })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.exportCsv(1, 'video.mp4')
    })

    expect(api.get).toHaveBeenCalledWith(
      '/export/timeline/video/1',
      { responseType: 'blob' }
    )
  })

  it('exportCsv calls downloadCsv with blob', async () => {
    const mockBlob = new Blob(['data'])
    api.get.mockResolvedValue({ data: mockBlob })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.exportCsv(1, 'video.mp4')
    })

    expect(downloadModule.downloadCsv).toHaveBeenCalled()
  })

  it('reprocess calls POST /videos/{id}/reprocess', async () => {
    api.post.mockResolvedValue({ data: {} })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.reprocess(1)
    })

    expect(api.post).toHaveBeenCalledWith('/videos/1/reprocess')
  })

  it('softDelete calls DELETE /videos/{id}', async () => {
    api.delete.mockResolvedValue({ data: {} })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.softDelete(1)
    })

    expect(api.delete).toHaveBeenCalledWith('/videos/1')
  })

  it('restore calls POST /videos/{id}/restore', async () => {
    api.post.mockResolvedValue({ data: {} })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.restore(1)
    })

    expect(api.post).toHaveBeenCalledWith('/videos/1/restore')
  })

  it('loadingId is set during call and cleared after', async () => {
    api.post.mockResolvedValue({ data: {} })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    expect(result.current.loadingId).toBeNull()

    act(() => {
      result.current.reprocess(1)
    })

    // loadingId is set synchronously after call
    expect(result.current.loadingId).toBe(1)

    await waitFor(() => {
      expect(result.current.loadingId).toBeNull()
    })
  })

  it('loadingAction is set during call and cleared after', async () => {
    api.post.mockResolvedValue({ data: {} })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    expect(result.current.loadingAction).toBeNull()

    act(() => {
      result.current.reprocess(1)
    })

    expect(result.current.loadingAction).toBe('reprocess')

    await waitFor(() => {
      expect(result.current.loadingAction).toBeNull()
    })
  })

  it('onSuccess called with action and videoId after success', async () => {
    api.post.mockResolvedValue({ data: {} })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.reprocess(1)
    })

    expect(mockOnSuccess).toHaveBeenCalledWith('reprocess', 1)
  })

  it('onError called with action and error message after failure', async () => {
    const errorMessage = 'Arquivo não encontrado'
    api.post.mockRejectedValue({
      response: { data: { detail: errorMessage } },
    })

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.reprocess(1)
    })

    expect(mockOnError).toHaveBeenCalledWith('reprocess', errorMessage)
  })

  it('handles error without response data', async () => {
    api.post.mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => useVideoActions({
      onSuccess: mockOnSuccess,
      onError: mockOnError,
    }))

    await act(async () => {
      await result.current.reprocess(1)
    })

    expect(mockOnError).toHaveBeenCalledWith('reprocess', 'Network error')
  })
})
