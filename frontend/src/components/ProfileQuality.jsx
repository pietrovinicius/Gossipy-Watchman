import { useEffect, useState } from 'react'
import api from '../services/api'

const SIGNAL_CLASSES = {
  green: 'bg-success',
  yellow: 'bg-amber-400',
  red: 'bg-error-color',
}

const TEXT_CLASSES = {
  green: 'text-success',
  yellow: 'text-amber-500 dark:text-amber-400',
  red: 'text-error-color',
}

export default function ProfileQuality({ personId }) {
  const [quality, setQuality] = useState(null)
  const [loadErr, setLoadErr] = useState('')

  useEffect(() => {
    setLoadErr('')
    setQuality(null)
    api.get(`/people/${personId}/quality`)
      .then((res) => setQuality(res.data))
      .catch(() => setLoadErr('Erro ao carregar qualidade do perfil.'))
  }, [personId])

  if (loadErr) {
    return (
      <div className="card">
        <p className="text-xs text-error-color">{loadErr}</p>
      </div>
    )
  }

  if (quality === null) {
    return (
      <div className="card">
        <div className="h-16 animate-pulse bg-border rounded-lg" />
      </div>
    )
  }

  const signalClass = SIGNAL_CLASSES[quality.color] ?? SIGNAL_CLASSES.red
  const textClass = TEXT_CLASSES[quality.color] ?? TEXT_CLASSES.red

  return (
    <div className="card">
      <h2 className="text-sm font-semibold text-text-base mb-3">Qualidade do perfil</h2>
      <div className="flex items-center gap-4">
        <span
          data-quality-signal={quality.color}
          className={`w-4 h-4 rounded-full flex-shrink-0 ${signalClass}`}
          aria-hidden="true"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-text-base">{Math.round(quality.quality_score)}%</span>
            <span className={`text-sm font-medium capitalize ${textClass}`}>{quality.quality_level}</span>
          </div>
          <p
            title={quality.recommendation}
            className="text-xs text-text-muted truncate mt-1"
          >
            {quality.recommendation}
          </p>
        </div>
      </div>
    </div>
  )
}
