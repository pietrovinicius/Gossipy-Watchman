import { useState, useEffect } from 'react'
import api from '../services/api'

export function useAuthImage(filename) {
  const [src, setSrc] = useState(null)

  useEffect(() => {
    if (!filename) return

    let objectUrl = null

    api.get(`/faces/${filename}`, { responseType: 'blob' })
      .then((res) => {
        objectUrl = URL.createObjectURL(res.data)
        setSrc(objectUrl)
      })
      .catch(() => setSrc(null))

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [filename])

  return src
}
