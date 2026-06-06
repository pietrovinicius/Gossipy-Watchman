import { useEffect, useRef, useState } from 'react'
import { BACKEND_URL } from '../services/api'

const WS_BASE = BACKEND_URL.replace(/^http/, 'ws')

export function useVideoWebSocket(videoId) {
  const [lastEvent, setLastEvent] = useState(null)
  const [wsStatus, setWsStatus] = useState('disconnected')
  const wsRef = useRef(null)

  useEffect(() => {
    if (videoId == null) return

    const token = sessionStorage.getItem('token') ?? ''
    const url = `${WS_BASE}/api/v1/ws/video/${videoId}?token=${token}`
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setWsStatus('connected')
    ws.onclose = () => setWsStatus('disconnected')
    ws.onerror = () => setWsStatus('disconnected')
    ws.onmessage = (e) => {
      try {
        setLastEvent(JSON.parse(e.data))
      } catch {
        // ignore malformed frames
      }
    }

    return () => {
      ws.onopen = null
      ws.onclose = null
      ws.onerror = null
      ws.onmessage = null
      ws.close()
    }
  }, [videoId])

  return { lastEvent, wsStatus }
}
