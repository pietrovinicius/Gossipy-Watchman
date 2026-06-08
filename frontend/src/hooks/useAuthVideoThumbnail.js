import { useState, useEffect } from 'react'
import api from '../services/api'

export function useAuthVideoThumbnail(videoId, hasThumbnail) {
  const [src, setSrc] = useState(null)

  useEffect(() => {
    if (!videoId || !hasThumbnail) return

    let objectUrl = null

    api.get(`/videos/${videoId}/thumbnail`, { responseType: 'blob' })
      .then((res) => {
        objectUrl = URL.createObjectURL(res.data)
        setSrc(objectUrl)
      })
      .catch(() => setSrc(null))

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [videoId, hasThumbnail])

  return src
}
