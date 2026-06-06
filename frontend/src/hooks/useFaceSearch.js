import { useState, useCallback } from 'react'
import api from '../services/api'

export function useFaceSearch() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [queryTimeMs, setQueryTimeMs] = useState(null)

  const search = useCallback(async (file) => {
    if (!file) {
      setError('Nenhum arquivo selecionado.')
      return
    }

    setLoading(true)
    setError(null)
    setResults([])
    setQueryTimeMs(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await api.post('/search/by-face', formData)
      setResults(res.data.results)
      setQueryTimeMs(res.data.query_time_ms)
    } catch (err) {
      setError(err.message || 'Erro ao buscar face.')
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setResults([])
    setError(null)
    setQueryTimeMs(null)
  }, [])

  return { results, loading, error, queryTimeMs, search, reset }
}
