import { useCallback, useEffect, useState } from 'react'
import { ImageOff, Star } from 'lucide-react'
import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'

function FrameThumb({ frame, onSetPrimary, settingFilename }) {
  const imgSrc = useAuthImage(frame.filename)
  const isSetting = settingFilename === frame.filename

  return (
    <div className="group relative aspect-square rounded-xl overflow-hidden bg-surface border border-border">
      {imgSrc ? (
        <img src={imgSrc} alt={`Amostra facial ${frame.filename}`} className="w-full h-full object-cover" />
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          <ImageOff className="w-6 h-6 text-text-muted" aria-hidden="true" />
        </div>
      )}

      {frame.is_primary && (
        <span className="absolute top-2 left-2 flex items-center gap-1 text-[10px] font-semibold
                         px-2 py-0.5 rounded-full bg-primary text-white">
          <Star className="w-3 h-3" aria-hidden="true" />
          Principal
        </span>
      )}

      {!frame.is_primary && (
        <button
          onClick={() => onSetPrimary(frame.filename)}
          disabled={isSetting}
          className="absolute inset-x-2 bottom-2 opacity-0 group-hover:opacity-100 focus-visible:opacity-100
                     transition-opacity duration-200 text-xs font-medium px-2 py-1.5 rounded-lg
                     bg-black/70 text-white hover:bg-black/80 cursor-pointer disabled:opacity-50
                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        >
          {isSetting ? 'Definindo…' : 'Definir como principal'}
        </button>
      )}
    </div>
  )
}

export default function PersonFrames({ personId }) {
  const [frames, setFrames] = useState(null)
  const [loadErr, setLoadErr] = useState('')
  const [settingFilename, setSettingFilename] = useState(null)
  const [actionErr, setActionErr] = useState('')

  const fetchFrames = useCallback(() => {
    setLoadErr('')
    api.get(`/people/${personId}/frames`)
      .then((res) => setFrames(res.data))
      .catch((err) => setLoadErr(err.message))
  }, [personId])

  useEffect(() => {
    fetchFrames()
  }, [fetchFrames])

  async function handleSetPrimary(filename) {
    setSettingFilename(filename)
    setActionErr('')
    try {
      await api.patch(`/people/${personId}/primary-photo`, { filename })
      fetchFrames()
    } catch {
      setActionErr('Erro ao definir foto principal.')
    } finally {
      setSettingFilename(null)
    }
  }

  return (
    <div className="card p-0 overflow-hidden">
      <div className="px-4 py-3 border-b border-border">
        <h2 className="text-sm font-semibold text-text-base">Frames detectados</h2>
      </div>
      <div className="p-4">
        {loadErr && <p className="text-xs text-error-color mb-3">{loadErr}</p>}
        {actionErr && <p className="text-xs text-error-color mb-3">{actionErr}</p>}

        {frames === null ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {Array.from({ length: 4 }, (_, i) => (
              <div key={i} className="aspect-square rounded-xl bg-border animate-pulse" />
            ))}
          </div>
        ) : frames.length === 0 ? (
          <p className="text-sm text-text-muted text-center py-8">
            Nenhum frame detectado para esta pessoa ainda.
          </p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {frames.map((frame) => (
              <FrameThumb
                key={frame.filename}
                frame={frame}
                onSetPrimary={handleSetPrimary}
                settingFilename={settingFilename}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
