import { useEffect, useRef } from 'react'
import { BACKEND_URL } from '../services/api'

const WS_BASE = BACKEND_URL.replace(/^http/, 'ws')

export function useGlobalWebSocket({ onEvent } = {}) {
  const wsRef = useRef(null)

  useEffect(() => {
    const token = sessionStorage.getItem('token') ?? ''
    const url = `${WS_BASE}/api/v1/ws/global?token=${token}`
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data)
        onEvent?.(payload)
      } catch {
        // ignore malformed frames
      }
    }

    return () => {
      ws.onmessage = null
      ws.close()
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return wsRef
}
