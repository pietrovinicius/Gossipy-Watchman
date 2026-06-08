import { useEffect, useState, useCallback, useMemo, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft, Download, Loader2, AlertCircle, UserCircle, ExternalLink,
  Users, Film, Clock, Activity, Trash2, RotateCcw, RotateCw, PlayCircle,
} from 'lucide-react'
import Layout from '../components/Layout'
import CategoryBadge from '../components/CategoryBadge'
import ConfirmModal from '../components/ConfirmModal'
import { VideoPlayer } from '../components/VideoPlayer'
import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'
import { sanitizeFileName } from '../utils/sanitizeFileName'
import { downloadCsv } from '../utils/downloadCsv'
import { formatDateTime } from '../utils/formatDate'

const STATUS_BADGE = {
  Pendente:    { cls: 'bg-warning/20 text-warning',       label: 'Pendente' },
  Processando: { cls: 'bg-processing/20 text-processing', label: 'Processando' },
  Concluído:   { cls: 'bg-success/20 text-success',       label: 'Concluído' },
  Erro:        { cls: 'bg-error-color/20 text-error-color', label: 'Erro' },
}

const REPROCESSABLE_STATUSES = ['Concluído', 'Erro']
const REFRESH_INTERVAL_MS = 10000
const TIMELINE_PREVIEW_COUNT = 3

function StatusBadge({ status }) {
  const cfg = STATUS_BADGE[status] ?? { cls: 'bg-border text-text-muted', label: status }
  return <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
}

function fmtSec(s) {
  return s != null ? `${Number(s).toFixed(1)}s` : '—'
}

function fmt3(n) {
  return Number(n).toFixed(3)
}

function fmtDuration(totalSeconds) {
  const total = Math.round(totalSeconds ?? 0)
  const minutes = Math.floor(total / 60)
  const seconds = total % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

function SummaryCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
        <Icon className="w-6 h-6" aria-hidden="true" />
      </div>
      <div>
        <p className="text-text-muted text-sm">{label}</p>
        <p className="text-2xl font-bold font-mono text-text-base">{value}</p>
      </div>
    </div>
  )
}

function PersonCard({ person, isOnScreen, onSeekTo, cardRef }) {
  const filename = person.profile_image_path
    ? person.profile_image_path.split('/').pop()
    : null
  const imgSrc = useAuthImage(filename)
  const [expanded, setExpanded] = useState(false)

  const collapsible = person.appearance_count > TIMELINE_PREVIEW_COUNT
  const visibleAppearances = expanded || !collapsible
    ? person.appearances
    : person.appearances.slice(0, TIMELINE_PREVIEW_COUNT)

  return (
    <div
      ref={cardRef}
      data-testid={`person-card-${person.person_id}`}
      className={`card space-y-4 transition-all ${isOnScreen ? 'border-2 border-primary' : ''}`}
    >
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 rounded-2xl overflow-hidden bg-surface border border-border flex-shrink-0">
          {imgSrc ? (
            <img src={imgSrc} alt={`Foto de ${person.person_name}`} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <UserCircle className="w-8 h-8 text-text-muted" aria-hidden="true" />
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-text-base truncate">{person.person_name}</h3>
            <CategoryBadge category={person.person_category} />
            {isOnScreen && (
              <span className="text-xs bg-primary text-white px-2 py-0.5 rounded-full animate-pulse">
                EM CENA
              </span>
            )}
          </div>
          <p className="text-xs text-text-muted">
            ID #{person.person_id} · {person.appearance_count} aparição{person.appearance_count === 1 ? '' : 'ões'}
          </p>
          <p className="text-xs text-text-muted">Presente por {fmtSec(person.total_seconds)}</p>
          <p className="text-xs text-text-muted">Primeira vez: {fmtSec(person.first_seen_at)} do vídeo</p>
          <p className="text-xs text-text-muted">Última vez: {fmtSec(person.last_seen_at)} do vídeo</p>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left px-3 py-2 text-text-muted font-medium text-xs">Início</th>
              <th className="text-left px-3 py-2 text-text-muted font-medium text-xs">Fim</th>
              <th className="text-left px-3 py-2 text-text-muted font-medium text-xs">Confiança</th>
            </tr>
          </thead>
          <tbody>
            {visibleAppearances.map((a) => (
              <tr
                key={a.id}
                onClick={() => onSeekTo?.(a.timestamp_start)}
                className="border-b border-border/50 last:border-b-0 cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
              >
                <td className="px-3 py-2 font-mono text-xs text-text-muted">{fmtSec(a.timestamp_start)}</td>
                <td className="px-3 py-2 font-mono text-xs text-text-muted">
                  {a.timestamp_end != null ? fmtSec(a.timestamp_end) : '—'}
                </td>
                <td className="px-3 py-2 font-mono text-xs text-text-muted">{fmt3(a.confidence)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {collapsible && !expanded && (
          <button
            onClick={() => setExpanded(true)}
            className="w-full text-center text-xs text-primary py-2 hover:underline cursor-pointer"
          >
            Ver todas as {person.appearance_count} aparições
          </button>
        )}
      </div>

      <div className="flex justify-between">
        <button
          onClick={() => onSeekTo?.(person.first_seen_at)}
          className="flex items-center gap-1.5 text-xs text-primary hover:underline"
        >
          <PlayCircle className="w-3.5 h-3.5" aria-hidden="true" />
          {fmtSec(person.first_seen_at)}
        </button>
        <Link
          to={`/people/${person.person_id}`}
          className="flex items-center gap-1.5 text-xs text-primary hover:underline"
        >
          Ver perfil completo
          <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
        </Link>
      </div>
    </div>
  )
}

export default function VideoDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const idRef = useRef(id)
  idRef.current = id
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState('')
  const [exportLoading, setExportLoading] = useState(false)
  const [exportErr, setExportErr] = useState('')
  const [actionErr, setActionErr] = useState('')
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [reprocessModalOpen, setReprocessModalOpen] = useState(false)
  const [seekTo, setSeekTo] = useState(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [videoDuration, setVideoDuration] = useState(0)

  const cardRefs = useRef({})
  const prevPeopleOnScreenRef = useRef([])

  const token = sessionStorage.getItem('token')

  const getPeopleOnScreen = (time, people) =>
    people?.filter(p =>
      p.appearances?.some(a =>
        a.timestamp_start <= time && (!a.timestamp_end || a.timestamp_end >= time)
      )
    ) || []

  const peopleOnScreen = useMemo(
    () => getPeopleOnScreen(currentTime, detail?.people),
    [currentTime, detail?.people]
  )

  const handlePlayClick = () => {
    setIsPlaying(true)
  }

  const handlePauseClick = () => {
    setIsPlaying(false)
  }

  const handleDurationChange = (duration) => {
    setVideoDuration(duration)
  }

  const fetchDetail = useCallback(() => {
    const requestedId = id
    setError('')
    return api.get(`/videos/${requestedId}/detail`)
      .then((res) => {
        // Descarta respostas que chegam fora de ordem (ex.: navegação rápida entre vídeos):
        // só aplica se a página ainda estiver no vídeo que originou esta requisição.
        if (idRef.current !== requestedId) return
        setDetail(res.data)
      })
      .catch((err) => {
        if (idRef.current !== requestedId) return
        setError(err.message)
      })
  }, [id])

  useEffect(() => {
    setDetail(null)
    setCurrentTime(0)
    setSeekTo(null)
    setVideoDuration(0)
    setIsPlaying(false)
    setError('')
    fetchDetail()
  }, [id, fetchDetail])

  const status = detail?.video?.status
  const isProcessing = status === 'Pendente' || status === 'Processando'

  useEffect(() => {
    if (!isProcessing) return
    const interval = setInterval(fetchDetail, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [isProcessing, fetchDetail])

  useEffect(() => {
    prevPeopleOnScreenRef.current = peopleOnScreen
  }, [peopleOnScreen])

  async function handleExportCsv() {
    setExportLoading(true)
    setExportErr('')
    try {
      const res = await api.get(`/export/timeline/video/${id}`, { responseType: 'blob' })
      const name = detail?.video?.file_name ? sanitizeFileName(detail.video.file_name) : 'video'
      downloadCsv(res.data, `gossipy_video_${id}_${name}.csv`)
    } catch {
      setExportErr('Erro ao exportar CSV.')
    } finally {
      setExportLoading(false)
    }
  }

  async function handleDeleteVideo() {
    setActionErr('')
    try {
      const res = await api.delete(`/videos/${id}`)
      setDetail((prev) => ({ ...prev, video: res.data }))
      setDeleteModalOpen(false)
    } catch (err) {
      setActionErr(err.response?.data?.detail ?? err.message)
      setDeleteModalOpen(false)
    }
  }

  async function handleRestoreVideo() {
    setActionErr('')
    try {
      await api.post(`/videos/${id}/restore`)
      fetchDetail()
    } catch (err) {
      setActionErr(err.response?.data?.detail ?? err.message)
    }
  }

  async function handleReprocessVideo() {
    setActionErr('')
    try {
      await api.post(`/videos/${id}/reprocess`)
      setReprocessModalOpen(false)
      fetchDetail()
    } catch (err) {
      setActionErr(err.response?.data?.detail ?? err.message)
      setReprocessModalOpen(false)
    }
  }

  if (error) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center py-24 gap-4 text-error-color">
          <AlertCircle className="w-10 h-10" aria-hidden="true" />
          <p className="text-sm">{error}</p>
          <button onClick={fetchDetail} className="btn-primary text-sm">
            Tentar novamente
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Player */}
        {detail && token && (
          <VideoPlayer
            key={id}
            videoId={parseInt(id)}
            token={token}
            onTimeUpdate={setCurrentTime}
            seekTo={seekTo}
            people={detail.people}
            duration={videoDuration}
            currentTime={currentTime}
            onSeek={setSeekTo}
            onDurationChange={handleDurationChange}
            onPlay={handlePlayClick}
            onPause={handlePauseClick}
          />
        )}

        {/* Header */}
        <div>
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-text-muted hover:text-text-base
                       transition-colors duration-200 cursor-pointer text-sm mb-3"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            Voltar para Dashboard
          </button>

          {detail === null ? (
            <div className="card h-24 animate-pulse" />
          ) : (
            <div className="card flex items-center justify-between gap-4 flex-wrap">
              <div className="space-y-1.5 min-w-0">
                <div className="flex items-center gap-3">
                  <h1 className="text-xl font-bold text-text-base truncate">
                    {sanitizeFileName(detail.video.file_name)}
                  </h1>
                  <StatusBadge status={detail.video.status} />
                </div>
                <p className="text-xs text-text-muted">Enviado em {formatDateTime(detail.video.uploaded_at)}</p>
              </div>
              <div className="flex items-center gap-2">
                {!detail.video.deleted_at && REPROCESSABLE_STATUSES.includes(detail.video.status) && (
                  <button
                    onClick={() => setReprocessModalOpen(true)}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                               border-border text-text-muted hover:text-text-base transition-colors"
                  >
                    <RotateCw className="w-3.5 h-3.5" aria-hidden="true" />
                    Reprocessar
                  </button>
                )}
                <button
                  onClick={handleExportCsv}
                  disabled={exportLoading}
                  className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                             border-border text-text-muted hover:text-text-base transition-colors
                             disabled:opacity-50"
                >
                  {exportLoading
                    ? <Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden="true" />
                    : <Download className="w-3.5 h-3.5" aria-hidden="true" />}
                  Exportar CSV
                </button>
                {detail.video.deleted_at ? (
                  <button
                    onClick={handleRestoreVideo}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                               border-border text-text-muted hover:text-text-base transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />
                    Restaurar vídeo
                  </button>
                ) : (
                  <button
                    onClick={() => setDeleteModalOpen(true)}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                               border-border text-error-color hover:bg-error-color/10 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
                    Excluir vídeo
                  </button>
                )}
              </div>
            </div>
          )}
          {exportErr && <p className="text-xs text-error-color mt-1">{exportErr}</p>}
          {actionErr && <p role="alert" className="text-xs text-error-color mt-1">{actionErr}</p>}
        </div>

        <ConfirmModal
          isOpen={deleteModalOpen}
          title="Excluir vídeo"
          message={detail ? `Esta ação excluirá o vídeo "${sanitizeFileName(detail.video.file_name)}". Digite "excluir" para confirmar. O vídeo pode ser restaurado posteriormente.` : ''}
          variant="danger"
          requireTyping
          confirmWord="excluir"
          onConfirm={handleDeleteVideo}
          onCancel={() => setDeleteModalOpen(false)}
        />

        <ConfirmModal
          isOpen={reprocessModalOpen}
          title="Reprocessar vídeo"
          message={detail ? `O status de "${sanitizeFileName(detail.video.file_name)}" voltará para Pendente e o worker de visão computacional será disparado novamente. Aparições anteriores serão substituídas.` : ''}
          variant="warning"
          confirmLabel="Reprocessar"
          onConfirm={handleReprocessVideo}
          onCancel={() => setReprocessModalOpen(false)}
        />

        {/* Summary cards */}
        {detail === null ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }, (_, i) => <div key={i} className="card h-20 animate-pulse" />)}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <SummaryCard icon={Users} label="Pessoas identificadas" value={detail.summary.total_people}
              color="bg-primary/20 text-primary" />
            <SummaryCard icon={Activity} label="Total de aparições" value={detail.summary.total_appearances}
              color="bg-purple-500/15 text-purple-400" />
            <SummaryCard icon={Clock} label="Tempo coberto" value={fmtDuration(detail.summary.duration_covered)}
              color="bg-warning/20 text-warning" />
            <SummaryCard icon={Film} label="Status" value={<StatusBadge status={detail.summary.processing_status} />}
              color="bg-success/20 text-success" />
          </div>
        )}

        {/* People section */}
        <div>
          <h2 className="text-sm font-semibold text-text-base mb-3">Pessoas neste vídeo</h2>

          {detail === null ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }, (_, i) => <div key={i} className="card h-32 animate-pulse" />)}
            </div>
          ) : isProcessing ? (
            <div className="card flex flex-col items-center justify-center gap-3 py-12 text-text-muted">
              <Loader2 className="w-8 h-8 animate-spin text-primary" aria-hidden="true" />
              <p className="text-sm">Vídeo ainda sendo processado. Aguarde...</p>
            </div>
          ) : detail.people.length === 0 ? (
            <div className="card text-center py-12 space-y-2">
              <p className="text-sm text-text-base">Nenhuma face identificada neste vídeo.</p>
              <p className="text-xs text-text-muted">
                Dica: se esperava encontrar pessoas, tente ajustar o FACE_RECOGNITION_TOLERANCE no .env para um valor maior.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {detail.people.map((person) => (
                <PersonCard
                  key={person.person_id}
                  person={person}
                  isOnScreen={peopleOnScreen?.some(p => p.person_id === person.person_id)}
                  onSeekTo={setSeekTo}
                  cardRef={(el) => { cardRefs.current[person.person_id] = el }}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
