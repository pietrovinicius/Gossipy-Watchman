import { useState, useRef, useEffect } from 'react'

export function VideoPlayer({ videoId, token, onTimeUpdate, seekTo }) {
  const videoRef = useRef(null)
  const [error, setError] = useState(null)
  const [playbackRate, setPlaybackRate] = useState(1)

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const videoUrl = `${apiUrl}/api/v1/videos/${videoId}/stream?token=${token}`

  useEffect(() => {
    if (seekTo !== null && seekTo !== undefined && videoRef.current) {
      videoRef.current.currentTime = seekTo
      videoRef.current.play()
    }
  }, [seekTo])

  const handleTimeUpdate = (e) => {
    onTimeUpdate?.(e.target.currentTime)
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

  return (
    <div className="w-full space-y-3">
      <div className="relative w-full bg-black rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          src={videoUrl}
          controls
          className="w-full max-h-[480px] object-contain"
          onTimeUpdate={handleTimeUpdate}
          onError={handleError}
          preload="metadata"
        />
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/80 text-white text-sm">
            {error}
          </div>
        )}
      </div>

      <div className="flex gap-2">
        {[0.5, 1, 1.5, 2].map((speed) => (
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
