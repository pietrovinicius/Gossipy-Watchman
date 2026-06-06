import { renderHook, act } from '@testing-library/react'
import { beforeEach, afterEach, describe, it, expect, vi } from 'vitest'

// Mock WebSocket global
class MockWebSocket {
  static instances = []

  constructor(url) {
    this.url = url
    this.readyState = 0 // CONNECTING
    this.onopen = null
    this.onmessage = null
    this.onclose = null
    this.onerror = null
    MockWebSocket.instances.push(this)
  }

  send(data) {
    this._sent = (this._sent || []).concat(data)
  }

  close() {
    this.readyState = 3 // CLOSED
    this.onclose?.({ code: 1000, reason: '' })
  }

  // helpers to simulate server events
  triggerOpen() {
    this.readyState = 1
    this.onopen?.({})
  }

  triggerMessage(data) {
    this.onmessage?.({ data: JSON.stringify(data) })
  }
}

let originalWebSocket

beforeEach(() => {
  MockWebSocket.instances = []
  originalWebSocket = global.WebSocket
  global.WebSocket = MockWebSocket
  sessionStorage.setItem('token', 'fake-jwt-token')
})

afterEach(() => {
  global.WebSocket = originalWebSocket
  sessionStorage.clear()
  vi.useRealTimers()
})

describe('useVideoWebSocket', () => {
  it('conecta na URL correta com token', async () => {
    const { useVideoWebSocket } = await import('../hooks/useVideoWebSocket.js')
    renderHook(() => useVideoWebSocket(7))

    expect(MockWebSocket.instances).toHaveLength(1)
    const ws = MockWebSocket.instances[0]
    expect(ws.url).toContain('/ws/video/7')
    expect(ws.url).toContain('token=fake-jwt-token')
  })

  it('retorna wsStatus "connected" após conexão aberta', async () => {
    const { useVideoWebSocket } = await import('../hooks/useVideoWebSocket.js')
    const { result } = renderHook(() => useVideoWebSocket(7))

    act(() => MockWebSocket.instances[0].triggerOpen())

    expect(result.current.wsStatus).toBe('connected')
  })

  it('retorna lastEvent ao receber mensagem do servidor', async () => {
    const { useVideoWebSocket } = await import('../hooks/useVideoWebSocket.js')
    const { result } = renderHook(() => useVideoWebSocket(7))

    act(() => MockWebSocket.instances[0].triggerOpen())
    act(() => MockWebSocket.instances[0].triggerMessage({ event: 'frame', second: 3 }))

    expect(result.current.lastEvent).toEqual({ event: 'frame', second: 3 })
  })

  it('não conecta se videoId for null/undefined', async () => {
    const { useVideoWebSocket } = await import('../hooks/useVideoWebSocket.js')
    renderHook(() => useVideoWebSocket(null))

    expect(MockWebSocket.instances).toHaveLength(0)
  })
})

describe('useGlobalWebSocket', () => {
  it('conecta na URL /ws/global com token', async () => {
    const { useGlobalWebSocket } = await import('../hooks/useGlobalWebSocket.js')
    renderHook(() => useGlobalWebSocket())

    expect(MockWebSocket.instances).toHaveLength(1)
    const ws = MockWebSocket.instances[0]
    expect(ws.url).toContain('/ws/global')
    expect(ws.url).toContain('token=fake-jwt-token')
  })

  it('chama onEvent com payload ao receber mensagem', async () => {
    const { useGlobalWebSocket } = await import('../hooks/useGlobalWebSocket.js')
    const onEvent = vi.fn()
    renderHook(() => useGlobalWebSocket({ onEvent }))

    act(() => MockWebSocket.instances[0].triggerOpen())
    act(() => MockWebSocket.instances[0].triggerMessage({ event: 'status', status: 'Concluído', video_id: 3 }))

    expect(onEvent).toHaveBeenCalledWith({ event: 'status', status: 'Concluído', video_id: 3 })
  })
})
