import { useState, useRef, useEffect } from 'react'

export function VideoPlayer({
  videoId,
  token,
  onTimeUpdate,
  seekTo,
  people = [],
  duration = 0,
  currentTime = 0,
  onSeek,
  onDurationChange,
  onPlay,
  onPause,
}) {
  const videoRef = useRef(null)
  const [error, setError] = useState(null)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [videoDuration, setVideoDuration] = useState(duration)

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const videoUrl = `${apiUrl}/api/v1/videos/${videoId}/stream?token=${token}`

  const getCategoryColor = (category) => {
    const map = {
      'Funcionário': '#3B82F6',
      'Visitante': '#8B5CF6',
      'Monitorado': '#EF4444',
      'Desconhecido': '#6B7280',
    }
    return map[category] || '#6B7280'
  }

  useEffect(() => {
    if (seekTo !== null && seekTo !== undefined && videoRef.current) {
      videoRef.current.currentTime = seekTo
      videoRef.current.play()
    }
  }, [seekTo])

  const handleTimeUpdate = (e) => {
    onTimeUpdate?.(e.target.currentTime)
  }

  const handleLoadedMetadata = (e) => {
    const dur = e.target.duration
    setVideoDuration(dur)
    onDurationChange?.(dur)
  }

  const handleError = () => {
    setError('Erro ao carregar vídeo. Verifique se o servidor está online.')
  }

  const handleSpeedClick = (speed) => {
    setPlaybackRate(speed)
    if (videoRef.current) {
      videoRef.current.playbackRate = speed
    }
  }

  const handlePlayClick = () => {
    onPlay?.()
  }

  const handlePauseClick = () => {
    onPause?.()
  }

  const handleSeek = (timestamp) => {
    onSeek?.(timestamp)
    if (videoRef.current) {
      videoRef.current.currentTime = timestamp
    }
  }

  return (
    <div className="w-full space-y-3">
      <div className="relative w-full bg-black rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          src={videoUrl}
          controls
          className="w-full max-h-[480px] object-contain"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onError={handleError}
          onPlay={handlePlayClick}
          onPause={handlePauseClick}
          preload="metadata"
        />
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/80 text-white text-sm">
            {error}
          </div>
        )}
      </div>

      {videoDuration > 0 && (
        <div className="space-y-2">
          <div
            data-testid="presence-bar"
            className="relative w-full h-3 bg-slate-200 dark:bg-slate-700 rounded-full mt-3 overflow-visible"
          >
            {people.map((person) =>
              person.appearances.map((app) => {
                const start = (app.timestamp_start / videoDuration) * 100
                const end = app.timestamp_end
                  ? (app.timestamp_end / videoDuration) * 100
                  : ((app.timestamp_start + 1) / videoDuration) * 100
                const width = Math.max(end - start, 0.5)
                const color = getCategoryColor(person.person_category)

                return (
                  <div
                    key={app.id}
                    data-testid={`presence-segment-${app.id}`}
                    className="absolute top-0 h-full rounded-sm opacity-80 hover:opacity-100 cursor-pointer transition-opacity"
                    style={{
                      left: `${start}%`,
                      width: `${width}%`,
                      backgroundColor: color,
                    }}
                    title={`${person.person_name}: ${app.timestamp_start}s`}
                    onClick={() => handleSeek(app.timestamp_start)}
                  />
                )
              })
            )}

            {videoDuration > 0 && (
              <div
                data-testid="presence-playhead"
                className="absolute top-[-4px] w-[3px] h-5 bg-red-500 rounded-full shadow-md pointer-events-none transition-[left] duration-100"
                style={{ left: `${(currentTime / videoDuration) * 100}%` }}
              />
            )}
          </div>

          <div className="text-xs text-text-muted space-x-3">
            {people.map((person) => (
              <span
                key={person.person_id}
                className="inline-flex items-center gap-1"
              >
                <span
                  className="w-2 h-2 rounded-full inline-block"
                  style={{ backgroundColor: getCategoryColor(person.person_category) }}
                />
                {person.person_name}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-2">
        {[0.5, 1, 1.5, 2, 6, 10, 25].map((speed) => (
          <button
            key={speed}
            onClick={() => handleSpeedClick(speed)}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              playbackRate === speed
                ? 'bg-primary text-white'
                : 'bg-card text-text-base border border-border hover:bg-card/80'
            }`}
          >
            {speed}x
          </button>
        ))}
      </div>
    </div>
  )
}
