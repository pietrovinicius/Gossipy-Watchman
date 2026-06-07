import { useState, useCallback } from 'react'
import api from '../services/api'
import { downloadCsv } from '../utils/downloadCsv'
import { sanitizeFileName } from '../utils/sanitizeFileName'

export function useVideoActions({ onSuccess, onError }) {
  const [loadingId, setLoadingId] = useState(null)
  const [loadingAction, setLoadingAction] = useState(null)

  const exportCsv = useCallback(
    async (videoId, fileName) => {
      setLoadingId(videoId)
      setLoadingAction('export')
      try {
        const res = await api.get(`/export/timeline/video/${videoId}`, { responseType: 'blob' })
        downloadCsv(res.data, `gossipy_video_${videoId}_${sanitizeFileName(fileName)}.csv`)
        onSuccess?.('export', videoId)
      } catch (err) {
        const message = err.response?.data?.detail ?? err.message
        onError?.('export', message)
      } finally {
        setLoadingId(null)
        setLoadingAction(null)
      }
    },
    [onSuccess, onError]
  )

  const reprocess = useCallback(
    async (videoId) => {
      setLoadingId(videoId)
      setLoadingAction('reprocess')
      try {
        await api.post(`/videos/${videoId}/reprocess`)
        onSuccess?.('reprocess', videoId)
      } catch (err) {
        const message = err.response?.data?.detail ?? err.message
        onError?.('reprocess', message)
      } finally {
        setLoadingId(null)
        setLoadingAction(null)
      }
    },
    [onSuccess, onError]
  )

  const softDelete = useCallback(
    async (videoId) => {
      setLoadingId(videoId)
      setLoadingAction('delete')
      try {
        await api.delete(`/videos/${videoId}`)
        onSuccess?.('delete', videoId)
      } catch (err) {
        const message = err.response?.data?.detail ?? err.message
        onError?.('delete', message)
      } finally {
        setLoadingId(null)
        setLoadingAction(null)
      }
    },
    [onSuccess, onError]
  )

  const restore = useCallback(
    async (videoId) => {
      setLoadingId(videoId)
      setLoadingAction('restore')
      try {
        await api.post(`/videos/${videoId}/restore`)
        onSuccess?.('restore', videoId)
      } catch (err) {
        const message = err.response?.data?.detail ?? err.message
        onError?.('restore', message)
      } finally {
        setLoadingId(null)
        setLoadingAction(null)
      }
    },
    [onSuccess, onError]
  )

  return {
    exportCsv,
    reprocess,
    softDelete,
    restore,
    loadingId,
    loadingAction,
  }
}
