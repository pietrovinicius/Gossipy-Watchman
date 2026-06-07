import { useState, useCallback, useRef } from 'react'

export function useUploadProgress() {
  const [progress, setProgress] = useState(0)
  const [speed, setSpeed] = useState(0)
  const [loaded, setLoaded] = useState(0)
  const [total, setTotal] = useState(0)
  const [eta, setEta] = useState(null)
  const startTimeRef = useRef(null)
  const lastLoadedRef = useRef(0)
  const lastTimeRef = useRef(null)

  const onUploadProgress = useCallback((progressEvent) => {
    const { loaded: currentLoaded, total: currentTotal } = progressEvent

    if (!startTimeRef.current) {
      startTimeRef.current = Date.now()
      lastTimeRef.current = Date.now()
      lastLoadedRef.current = 0
    }

    const now = Date.now()
    const timeDelta = (now - lastTimeRef.current) / 1000
    const bytesDelta = currentLoaded - lastLoadedRef.current

    const instantSpeed = timeDelta > 0 ? bytesDelta / timeDelta : 0
    const remaining = currentTotal - currentLoaded
    const etaSeconds = instantSpeed > 0 ? Math.ceil(remaining / instantSpeed) : null

    setProgress(Math.round((currentLoaded / currentTotal) * 100))
    setSpeed(instantSpeed)
    setLoaded(currentLoaded)
    setTotal(currentTotal)
    setEta(etaSeconds)

    lastLoadedRef.current = currentLoaded
    lastTimeRef.current = now
  }, [])

  const reset = useCallback(() => {
    setProgress(0)
    setSpeed(0)
    setLoaded(0)
    setTotal(0)
    setEta(null)
    startTimeRef.current = null
    lastLoadedRef.current = 0
    lastTimeRef.current = null
  }, [])

  return { progress, speed, loaded, total, eta, onUploadProgress, reset }
}
