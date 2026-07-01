import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

const MAX_NATIVE_RATE = 16
const HIGH_SPEED_INTERVAL_MS = 200

export function VideoPlayer({
  videoId,
  token,
  onTimeUpdate,
  seekTo,
  pauseSeekTo,
  people = [],
  duration = 0,
  currentTime = 0,
  onSeek,
  onSegmentSeek,
  onDurationChange,
  onPlay,
  onPause,
}) {
  const { t } = useTranslation()
  const videoRef = useRef(null)
  const highSpeedIntervalRef = useRef(null)
  const [error, setError] = useState(null)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [videoDuration, setVideoDuration] = useState(duration)
  const [legendExpanded, setLegendExpanded] = useState(false)

  const LEGEND_THRESHOLD = 5

  const clearHighSpeedInterval = () => {
    if (highSpeedIntervalRef.current) {
      clearInterval(highSpeedIntervalRef.current)
      highSpeedIntervalRef.current = null
    }
  }

  useEffect(() => {
    return () => clearHighSpeedInterval()
  }, [])

  const apiUrl =
    import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8002`
  const videoUrl = `${apiUrl}/api/v1/videos/${videoId}/stream?token=${token}`

  const getCategoryColor = (category) => {
    const map = {
      'Funcionário': '#3B82F6',
      'Visitante': '#8B5CF6',
      'Monitorado': '#EF4444',
      'Desconhecido': '#334155',
    }
    return map[category] || '#334155'
  }

  useEffect(() => {
    if (seekTo !== null && seekTo !== undefined && videoRef.current) {
      videoRef.current.currentTime = seekTo
      videoRef.current.play()
    }
  }, [seekTo])

  useEffect(() => {
    if (pauseSeekTo?.time != null && videoRef.current) {
      videoRef.current.currentTime = pauseSeekTo.time
      videoRef.current.pause()
    }
  }, [pauseSeekTo])

  const handleTimeUpdate = (e) => {
    onTimeUpdate?.(e.target.currentTime)
  }

  const handleLoadedMetadata = (e) => {
    const dur = e.target.duration
    setVideoDuration(dur)
    onDurationChange?.(dur)
  }

  const handleError = () => {
    setError(t('videoDetail.loadError'))
  }

  const handleSpeedClick = (speed) => {
    const wasHighSpeed = playbackRate > MAX_NATIVE_RATE
    clearHighSpeedInterval()
    setPlaybackRate(speed)

    if (!videoRef.current) return

    if (speed <= MAX_NATIVE_RATE) {
      videoRef.current.playbackRate = speed
      if (wasHighSpeed) {
        videoRef.current.play()
      }
    } else {
      videoRef.current.pause()
      videoRef.current.playbackRate = 1
      const seekStep = speed * (HIGH_SPEED_INTERVAL_MS / 1000)
      highSpeedIntervalRef.current = setInterval(() => {
        if (!videoRef.current) { clearHighSpeedInterval(); return }
        const newTime = videoRef.current.currentTime + seekStep
        const dur = videoRef.current.duration || 0
        if (newTime >= dur) {
          videoRef.current.currentTime = dur
          clearHighSpeedInterval()
        } else {
          videoRef.current.currentTime = newTime
        }
      }, HIGH_SPEED_INTERVAL_MS)
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
            className="relative w-full h-3 bg-slate-200 dark:bg-slate-700 rounded-full mt-3 overflow-visible cursor-pointer"
            onClick={(e) => {
              if (e.target !== e.currentTarget) return
              const rect = e.currentTarget.getBoundingClientRect()
              const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
              const time = ratio * videoDuration
              handleSeek(time)
              onSegmentSeek?.(null, time)
            }}
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
                    onClick={() => {
                      handleSeek(app.timestamp_start)
                      onSegmentSeek?.(person.person_id, app.timestamp_start)
                    }}
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

          {people.length > LEGEND_THRESHOLD ? (
            <div className="flex flex-col gap-1">
              <button
                data-testid="legend-toggle"
                onClick={() => setLegendExpanded(v => !v)}
                className="text-xs text-primary hover:underline self-start"
              >
                {legendExpanded
                  ? t('videoDetail.hideLegend')
                  : t('videoDetail.showLegend', { count: people.length })}
              </button>
              {legendExpanded && (
                <div className="text-xs text-text-muted flex flex-wrap gap-x-3 gap-y-1">
                  {people.map((person) => (
                    <span key={person.person_id} className="inline-flex items-center gap-1">
                      <span
                        className="w-2 h-2 rounded-full inline-block flex-shrink-0"
                        style={{ backgroundColor: getCategoryColor(person.person_category) }}
                      />
                      {person.person_name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-text-muted space-x-3">
              {people.map((person) => (
                <span key={person.person_id} className="inline-flex items-center gap-1">
                  <span
                    className="w-2 h-2 rounded-full inline-block"
                    style={{ backgroundColor: getCategoryColor(person.person_category) }}
                  />
                  {person.person_name}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2">
        {[0.5, 1, 1.5, 2, 6, 10, 25, 50, 100].map((speed) => (
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
