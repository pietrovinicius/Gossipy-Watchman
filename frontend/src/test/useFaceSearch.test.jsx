import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../services/api', () => ({
  default: {
    post: vi.fn(),
  },
  BACKEND_URL: 'http://localhost:8000',
}))

describe('useFaceSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('estado inicial: results=[], loading=false, error=null', async () => {
    const { useFaceSearch } = await import('../hooks/useFaceSearch.js')
    const { result } = renderHook(() => useFaceSearch())
    expect(result.current.results).toEqual([])
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('search() define loading=true durante requisição', async () => {
    const api = (await import('../services/api')).default
    let resolvePromise
    api.post.mockReturnValue(new Promise((res) => { resolvePromise = res }))

    const { useFaceSearch } = await import('../hooks/useFaceSearch.js')
    const { result } = renderHook(() => useFaceSearch())

    act(() => { result.current.search(new File(['x'], 'face.jpg', { type: 'image/jpeg' })) })

    expect(result.current.loading).toBe(true)

    // cleanup
    act(() => resolvePromise({ data: { results: [], query_time_ms: 0 } }))
  })

  it('search() preenche results com resposta da API', async () => {
    const api = (await import('../services/api')).default
    const MOCK_RESULTS = [
      { person_id: 1, person_name: 'Alice', distance: 0.2, confidence_pct: 80 },
    ]
    api.post.mockResolvedValue({ data: { results: MOCK_RESULTS, query_time_ms: 42 } })

    const { useFaceSearch } = await import('../hooks/useFaceSearch.js')
    const { result } = renderHook(() => useFaceSearch())

    await act(async () => {
      await result.current.search(new File(['x'], 'face.jpg', { type: 'image/jpeg' }))
    })

    expect(result.current.results).toEqual(MOCK_RESULTS)
    expect(result.current.loading).toBe(false)
    expect(result.current.queryTimeMs).toBe(42)
  })

  it('search() define error em caso de falha', async () => {
    const api = (await import('../services/api')).default
    api.post.mockRejectedValue(new Error('Nenhuma face detectada'))

    const { useFaceSearch } = await import('../hooks/useFaceSearch.js')
    const { result } = renderHook(() => useFaceSearch())

    await act(async () => {
      await result.current.search(new File(['x'], 'face.jpg', { type: 'image/jpeg' }))
    })

    expect(result.current.error).toBe('Nenhuma face detectada')
    expect(result.current.results).toEqual([])
  })

  it('reset() limpa results, error e queryTimeMs', async () => {
    const api = (await import('../services/api')).default
    api.post.mockResolvedValue({ data: { results: [{ person_id: 1 }], query_time_ms: 10 } })

    const { useFaceSearch } = await import('../hooks/useFaceSearch.js')
    const { result } = renderHook(() => useFaceSearch())

    await act(async () => {
      await result.current.search(new File(['x'], 'face.jpg', { type: 'image/jpeg' }))
    })

    act(() => result.current.reset())

    expect(result.current.results).toEqual([])
    expect(result.current.error).toBeNull()
    expect(result.current.queryTimeMs).toBeNull()
  })

  it('search() envia FormData com campo "file"', async () => {
    const api = (await import('../services/api')).default
    api.post.mockResolvedValue({ data: { results: [], query_time_ms: 5 } })

    const { useFaceSearch } = await import('../hooks/useFaceSearch.js')
    const { result } = renderHook(() => useFaceSearch())

    const file = new File(['x'], 'face.jpg', { type: 'image/jpeg' })
    await act(async () => { await result.current.search(file) })

    const [url, formData] = api.post.mock.calls[0]
    expect(url).toBe('/search/by-face')
    expect(formData).toBeInstanceOf(FormData)
  })

  it('search() rejeitada se nenhum arquivo passado', async () => {
    const api = (await import('../services/api')).default
    const { useFaceSearch } = await import('../hooks/useFaceSearch.js')
    const { result } = renderHook(() => useFaceSearch())

    await act(async () => { await result.current.search(null) })

    expect(api.post).not.toHaveBeenCalled()
    expect(result.current.error).toBeTruthy()
  })
})
