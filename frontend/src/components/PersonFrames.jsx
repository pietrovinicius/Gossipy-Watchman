import { useCallback, useEffect, useState } from 'react'
import { ImageOff, Star, Trash2 } from 'lucide-react'
import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'

function FrameThumb({ frame, onSetPrimary, onDelete, settingFilename, deletingFilename }) {
  // Cache-busting: quando is_primary muda, invalida cache no hook para refetch
  const cacheTag = frame.is_primary ? 'principal' : ''
  const imgSrc = useAuthImage(frame.filename, cacheTag)
  const isSetting = settingFilename === frame.filename
  const isDeleting = deletingFilename === frame.filename

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

      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 focus-visible:opacity-100
                      transition-opacity duration-200 flex flex-col items-center justify-end p-2 gap-2">
        {!frame.is_primary && (
          <button
            onClick={() => onSetPrimary(frame.filename)}
            disabled={isSetting || isDeleting}
            className="w-full text-xs font-medium px-2 py-1.5 rounded-lg
                       bg-primary text-white hover:bg-primary/90 cursor-pointer disabled:opacity-50
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            {isSetting ? 'Definindo…' : 'Definir como principal'}
          </button>
        )}
        <button
          onClick={() => onDelete(frame.filename)}
          disabled={isDeleting || isSetting}
          className="w-full flex items-center justify-center gap-1.5 text-xs font-medium px-2 py-1.5 rounded-lg
                     bg-error-color/80 text-white hover:bg-error-color cursor-pointer disabled:opacity-50
                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-error-color"
        >
          <Trash2 className="w-3 h-3" aria-hidden="true" />
          {isDeleting ? 'Deletando…' : 'Deletar'}
        </button>
      </div>
    </div>
  )
}

export default function PersonFrames({ personId }) {
  const [frames, setFrames] = useState(null)
  const [loadErr, setLoadErr] = useState('')
  const [settingFilename, setSettingFilename] = useState(null)
  const [deletingFilename, setDeletingFilename] = useState(null)
  const [actionErr, setActionErr] = useState('')

  useEffect(() => {
    console.log('[PersonFrames] frames estado mudou:', frames)
  }, [frames])

  const fetchFrames = useCallback(() => {
    setLoadErr('')
    api.get(`/people/${personId}/frames`)
      .then((res) => {
        console.log('[PersonFrames] fetchFrames resposta:', res.data)
        setFrames(res.data)
      })
      .catch((err) => {
        console.error('[PersonFrames] fetchFrames erro:', err)
        setLoadErr(err.message)
      })
  }, [personId])

  useEffect(() => {
    fetchFrames()
  }, [fetchFrames])

  async function handleSetPrimary(filename) {
    console.log('[PersonFrames] handleSetPrimary clicado:', filename)
    setSettingFilename(filename)
    setActionErr('')
    try {
      const patchRes = await api.patch(`/people/${personId}/primary-photo`, { filename })
      console.log('[PersonFrames] PATCH resposta:', patchRes.data)
      console.log('[PersonFrames] Chamando fetchFrames após PATCH')
      await fetchFrames()
    } catch (err) {
      console.error('[PersonFrames] handleSetPrimary erro:', err)
      setActionErr(err.response?.data?.detail ?? err.message ?? 'Erro ao definir foto principal.')
    } finally {
      setSettingFilename(null)
    }
  }

  async function handleDeleteFrame(filename) {
    setDeletingFilename(filename)
    setActionErr('')
    try {
      await api.delete(`/people/${personId}/frames/${filename}`)
      fetchFrames()
    } catch (err) {
      setActionErr(err.response?.data?.detail ?? err.message ?? 'Erro ao deletar frame.')
    } finally {
      setDeletingFilename(null)
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
                key={`${frame.filename}_${frame.is_primary}`}
                frame={frame}
                onSetPrimary={handleSetPrimary}
                onDelete={handleDeleteFrame}
                settingFilename={settingFilename}
                deletingFilename={deletingFilename}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
