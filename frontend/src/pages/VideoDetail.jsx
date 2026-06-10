import { useEffect, useState, useCallback, useMemo, useRef } from 'react'
import { useParams, useNavigate, useLocation, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  ArrowLeft, Download, Loader2, AlertCircle, UserCircle, ExternalLink,
  Users, Film, Clock, Activity, Trash2, RotateCcw, RotateCw, PlayCircle,
  UserPlus, X, Search,
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
  Pendente:    { cls: 'bg-warning/20 text-warning',       key: 'status.pending' },
  Processando: { cls: 'bg-processing/20 text-processing', key: 'status.processing' },
  Concluído:   { cls: 'bg-success/20 text-success',       key: 'status.completed' },
  Erro:        { cls: 'bg-error-color/20 text-error-color', key: 'status.error' },
}

const REPROCESSABLE_STATUSES = ['Concluído', 'Erro']
const REFRESH_INTERVAL_MS = 10000
const TIMELINE_PREVIEW_COUNT = 3

function StatusBadge({ status }) {
  const { t } = useTranslation()
  const cfg = STATUS_BADGE[status]
  return <span className={`badge ${cfg ? cfg.cls : 'bg-border text-text-muted'}`}>{cfg ? t(cfg.key) : status}</span>
}

function fmtMmSs(s) {
  if (s == null) return '—'
  const total = Math.round(Number(s))
  const m = Math.floor(total / 60)
  const sec = total % 60
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
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

function PersonCard({ person, isOnScreen, onSeekTo, onSeekAndPause, cardRef }) {
  const { t } = useTranslation()
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
                {t('videoDetail.inScene')}
              </span>
            )}
          </div>
          <p className="text-xs text-text-muted">
            ID #{person.person_id} · {t('videoDetail.appearances', { count: person.appearance_count })}
          </p>
          <p className="text-xs text-text-muted">{t('videoDetail.presentFor', { seconds: fmtMmSs(person.total_seconds) })}</p>
          <p className="text-xs text-text-muted">{t('videoDetail.firstSeenInVideo', { time: fmtMmSs(person.first_seen_at) })}</p>
          <p className="text-xs text-text-muted">{t('videoDetail.lastSeenInVideo', { time: fmtMmSs(person.last_seen_at) })}</p>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left px-3 py-2 text-text-muted font-medium text-xs">{t('videoDetail.start')}</th>
              <th className="text-left px-3 py-2 text-text-muted font-medium text-xs">{t('videoDetail.end')}</th>
              <th className="text-left px-3 py-2 text-text-muted font-medium text-xs">{t('videoDetail.confidence')}</th>
            </tr>
          </thead>
          <tbody>
            {visibleAppearances.map((a) => (
              <tr
                key={a.id}
                onClick={() => onSeekTo?.(a.timestamp_start)}
                className="border-b border-border/50 last:border-b-0 cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
              >
                <td className="px-3 py-2 font-mono text-xs text-text-muted">{fmtMmSs(a.timestamp_start)}</td>
                <td className="px-3 py-2 font-mono text-xs text-text-muted">
                  {a.timestamp_end != null ? fmtMmSs(a.timestamp_end) : '—'}
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
            {t('videoDetail.showAll', { count: person.appearance_count })}
          </button>
        )}
      </div>

      <div className="flex justify-between items-center flex-wrap gap-y-1">
        <div className="flex items-center gap-1 flex-wrap">
          <button
            onClick={() => onSeekTo?.(person.first_seen_at)}
            title={t('videoDetail.playFromFirstAppearance')}
            className="flex items-center text-primary hover:text-primary/70 transition-colors"
          >
            <PlayCircle className="w-3.5 h-3.5" aria-hidden="true" />
          </button>
          {visibleAppearances.map((a) => (
            <button
              key={a.id}
              onClick={() => onSeekAndPause?.(a.timestamp_start)}
              title={t('videoDetail.seekAndPause')}
              data-testid={`seek-pause-${person.person_id}-${a.id}`}
              className="text-xs text-primary font-mono hover:underline px-1 py-0.5 rounded border border-primary/30 hover:border-primary/70 transition-colors"
            >
              {fmtMmSs(a.timestamp_start)}
            </button>
          ))}
        </div>
        <Link
          to={`/people/${person.person_id}`}
          className="flex items-center gap-1.5 text-xs text-primary hover:underline"
        >
          {t('videoDetail.viewFullProfile')}
          <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
        </Link>
      </div>
    </div>
  )
}

function PersonPickerThumb({ person }) {
  const filename = person.profile_image_path ? person.profile_image_path.split('/').pop() : null
  const imgSrc = useAuthImage(filename)
  return (
    <div className="w-8 h-8 rounded-lg overflow-hidden bg-surface border border-border flex-shrink-0">
      {imgSrc
        ? <img src={imgSrc} alt="" className="w-full h-full object-cover" />
        : <div className="w-full h-full flex items-center justify-center">
            <UserCircle className="w-4 h-4 text-text-muted" />
          </div>
      }
    </div>
  )
}

function AddPersonModal({ isOpen, onClose, onSubmit, currentTime, isSubmitting, submitErr }) {
  const { t } = useTranslation()
  const [people, setPeople] = useState([])
  const [query, setQuery] = useState('')
  const [selectedPerson, setSelectedPerson] = useState(null)
  const [timestampStart, setTimestampStart] = useState('')
  const [timestampEnd, setTimestampEnd] = useState('')

  useEffect(() => {
    if (!isOpen) return
    setQuery('')
    setSelectedPerson(null)
    setTimestampStart(currentTime != null ? String(Number(currentTime).toFixed(1)) : '')
    setTimestampEnd('')
    api.get('/people?limit=200').then(res => setPeople(res.data)).catch(() => {})
  }, [isOpen, currentTime])

  const filtered = query.trim()
    ? people.filter(p => p.name.toLowerCase().includes(query.trim().toLowerCase()))
    : people

  function handleSubmit(e) {
    e.preventDefault()
    if (!selectedPerson) return
    onSubmit({
      person_id: selectedPerson.id,
      timestamp_start: parseFloat(timestampStart) || 0,
      timestamp_end: parseFloat(timestampEnd) || parseFloat(timestampStart) || 0,
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
         onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="bg-background border border-border rounded-2xl w-full max-w-md shadow-2xl
                      flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <h2 className="text-base font-semibold text-text-base">{t('videoDetail.addPersonTitle')}</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-base cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-5 overflow-y-auto">
          {/* Busca de pessoa */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-text-muted">{t('videoDetail.addPersonField')}</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="text"
                placeholder={t('videoDetail.addPersonSearchPlaceholder')}
                value={query}
                onChange={e => { setQuery(e.target.value); setSelectedPerson(null) }}
                className="w-full pl-9 pr-3 py-2 text-sm bg-surface border border-border rounded-lg
                           text-text-base placeholder:text-text-muted focus:outline-none focus:ring-2
                           focus:ring-primary"
              />
            </div>
            <div className="border border-border rounded-lg overflow-hidden max-h-44 overflow-y-auto">
              {filtered.length === 0
                ? <p className="text-xs text-text-muted text-center py-4">{t('videoDetail.addPersonNoResults')}</p>
                : filtered.map(p => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => { setSelectedPerson(p); setQuery(p.name) }}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-primary/10
                                transition-colors ${selectedPerson?.id === p.id ? 'bg-primary/15' : ''}`}
                  >
                    <PersonPickerThumb person={p} />
                    <span className="text-sm text-text-base truncate">{p.name}</span>
                    {p.category && <CategoryBadge category={p.category} />}
                  </button>
                ))
              }
            </div>
          </div>

          {/* Timestamps */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-text-muted">{t('videoDetail.startSeconds')}</label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={timestampStart}
                onChange={e => setTimestampStart(e.target.value)}
                required
                className="w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg
                           text-text-base focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-text-muted">{t('videoDetail.endSeconds')}</label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={timestampEnd}
                onChange={e => setTimestampEnd(e.target.value)}
                required
                className="w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg
                           text-text-base focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {submitErr && <p className="text-xs text-error-color">{submitErr}</p>}

          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose}
              className="flex-1 py-2 text-sm border border-border rounded-lg text-text-muted
                         hover:text-text-base transition-colors cursor-pointer">
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              disabled={!selectedPerson || isSubmitting}
              className="flex-1 py-2 text-sm bg-primary text-white rounded-lg
                         hover:bg-primary/90 disabled:opacity-50 cursor-pointer transition-colors"
            >
              {isSubmitting ? t('videoDetail.saving') : t('videoDetail.add')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function VideoDetail() {
  const { t } = useTranslation()
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const idRef = useRef(id)
  idRef.current = id
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState('')
  const [exportLoading, setExportLoading] = useState(false)
  const [exportErr, setExportErr] = useState('')
  const [actionErr, setActionErr] = useState('')
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [reprocessModalOpen, setReprocessModalOpen] = useState(false)
  const [addPersonModalOpen, setAddPersonModalOpen] = useState(false)
  const [addPersonSubmitting, setAddPersonSubmitting] = useState(false)
  const [addPersonErr, setAddPersonErr] = useState('')
  const [seekTo, setSeekTo] = useState(location.state?.seekTo ?? null)
  const [pauseSeekTo, setPauseSeekTo] = useState(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [videoDuration, setVideoDuration] = useState(0)

  const cardRefs = useRef({})
  const playerRef = useRef(null)
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

  const handleSeekClick = (ts) => {
    setSeekTo(ts)
    playerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const handleSeekAndPause = (ts) => {
    setPauseSeekTo({ time: ts })
    playerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const handleSegmentSeek = (person_id, ts) => {
    setSeekTo(ts)
    const visible = getPeopleOnScreen(ts, detail?.people)
    const targetId = (person_id != null && visible.some(p => p.person_id === person_id))
      ? person_id
      : (visible[0]?.person_id ?? person_id)
    if (targetId != null) {
      cardRefs.current[targetId]?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
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
    setPauseSeekTo(null)
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
      setExportErr(t('videoDetail.exportError'))
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

  async function handleAddPerson({ person_id, timestamp_start, timestamp_end }) {
    setAddPersonSubmitting(true)
    setAddPersonErr('')
    try {
      await api.post(`/videos/${id}/appearances`, { person_id, timestamp_start, timestamp_end, confidence: 0.0 })
      setAddPersonModalOpen(false)
      fetchDetail()
    } catch (err) {
      setAddPersonErr(err.response?.data?.detail ?? err.message ?? t('videoDetail.addPersonError'))
    } finally {
      setAddPersonSubmitting(false)
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
            {t('common.tryAgain')}
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-4">
        {/* Header — full width */}
        <div>
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-text-muted hover:text-text-base
                       transition-colors duration-200 cursor-pointer text-sm mb-3"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            {t('videoDetail.backToDashboard')}
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
                <p className="text-xs text-text-muted">{t('videoDetail.sentAt', { date: formatDateTime(detail.video.uploaded_at) })}</p>
              </div>
              <div className="flex items-center gap-2">
                {!detail.video.deleted_at && detail.video.status === 'Concluído' && (
                  <button
                    onClick={() => { setAddPersonErr(''); setAddPersonModalOpen(true) }}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                               border-primary text-primary hover:bg-primary/10 transition-colors"
                  >
                    <UserPlus className="w-3.5 h-3.5" aria-hidden="true" />
                    {t('videoDetail.addPerson')}
                  </button>
                )}
                {!detail.video.deleted_at && REPROCESSABLE_STATUSES.includes(detail.video.status) && (
                  <button
                    onClick={() => setReprocessModalOpen(true)}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                               border-border text-text-muted hover:text-text-base transition-colors"
                  >
                    <RotateCw className="w-3.5 h-3.5" aria-hidden="true" />
                    {t('videoDetail.reprocess')}
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
                  {t('videoDetail.exportCsv')}
                </button>
                {detail.video.deleted_at ? (
                  <button
                    onClick={handleRestoreVideo}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                               border-border text-text-muted hover:text-text-base transition-colors"
                  >
                    <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />
                    {t('videoDetail.restoreVideo')}
                  </button>
                ) : (
                  <button
                    onClick={() => setDeleteModalOpen(true)}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                               border-border text-error-color hover:bg-error-color/10 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
                    {t('videoDetail.deleteVideo')}
                  </button>
                )}
              </div>
            </div>
          )}
          {exportErr && <p className="text-xs text-error-color mt-1">{exportErr}</p>}
          {actionErr && <p role="alert" className="text-xs text-error-color mt-1">{actionErr}</p>}
        </div>

        {/* Summary cards — full width */}
        {detail === null ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }, (_, i) => <div key={i} className="card h-20 animate-pulse" />)}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <SummaryCard icon={Users} label={t('videoDetail.peopleIdentified')} value={detail.summary.total_people}
              color="bg-primary/20 text-primary" />
            <SummaryCard icon={Activity} label={t('videoDetail.totalAppearances')} value={detail.summary.total_appearances}
              color="bg-purple-500/15 text-purple-400" />
            <SummaryCard icon={Clock} label={t('videoDetail.timeCovered')} value={fmtDuration(detail.summary.duration_covered)}
              color="bg-warning/20 text-warning" />
            <SummaryCard icon={Film} label={t('videoDetail.status')} value={<StatusBadge status={detail.summary.processing_status} />}
              color="bg-success/20 text-success" />
          </div>
        )}

        {/* Split layout: player left (sticky) + people right */}
        <div data-testid="split-layout" className="flex gap-6 items-start">
          {/* Left column: player — sticky */}
          <div
            ref={playerRef}
            data-testid="player-sticky-wrapper"
            className="sticky top-4 self-start w-[58%] min-w-0"
          >
            {detail && token && (
              <VideoPlayer
                key={id}
                videoId={parseInt(id)}
                token={token}
                onTimeUpdate={setCurrentTime}
                seekTo={seekTo}
                pauseSeekTo={pauseSeekTo}
                people={detail.people}
                duration={videoDuration}
                currentTime={currentTime}
                onSeek={setSeekTo}
                onSegmentSeek={handleSegmentSeek}
                onDurationChange={handleDurationChange}
                onPlay={handlePlayClick}
                onPause={handlePauseClick}
              />
            )}
            {detail === null && <div className="card h-64 animate-pulse" />}
          </div>

          {/* Right column: people panel */}
          <div data-testid="people-panel" className="w-[42%] min-w-0 space-y-4">
            <h2 className="text-sm font-semibold text-text-base">{t('videoDetail.peopleInVideo')}</h2>

            {detail === null ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }, (_, i) => <div key={i} className="card h-32 animate-pulse" />)}
              </div>
            ) : isProcessing ? (
              <div className="card flex flex-col items-center justify-center gap-3 py-12 text-text-muted">
                <Loader2 className="w-8 h-8 animate-spin text-primary" aria-hidden="true" />
                <p className="text-sm">{t('videoDetail.processing')}</p>
              </div>
            ) : detail.people.length === 0 ? (
              <div className="card text-center py-12 space-y-2">
                <p className="text-sm text-text-base">{t('videoDetail.noFacesFound')}</p>
                <p className="text-xs text-text-muted">
                  {t('videoDetail.noFacesHint')}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {detail.people.map((person) => (
                  <PersonCard
                    key={person.person_id}
                    person={person}
                    isOnScreen={peopleOnScreen?.some(p => p.person_id === person.person_id)}
                    onSeekTo={handleSeekClick}
                    onSeekAndPause={handleSeekAndPause}
                    cardRef={(el) => { cardRefs.current[person.person_id] = el }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        <AddPersonModal
          isOpen={addPersonModalOpen}
          onClose={() => setAddPersonModalOpen(false)}
          onSubmit={handleAddPerson}
          currentTime={currentTime}
          isSubmitting={addPersonSubmitting}
          submitErr={addPersonErr}
        />

        <ConfirmModal
          isOpen={deleteModalOpen}
          title={t('videoDetail.deleteConfirmTitle')}
          message={detail ? t('videoDetail.deleteConfirmMessage', { name: sanitizeFileName(detail.video.file_name) }) : ''}
          variant="danger"
          requireTyping
          confirmWord={t('videoDetail.deleteConfirmWord')}
          onConfirm={handleDeleteVideo}
          onCancel={() => setDeleteModalOpen(false)}
        />

        <ConfirmModal
          isOpen={reprocessModalOpen}
          title={t('videoDetail.reprocessConfirmTitle')}
          message={detail ? t('videoDetail.reprocessConfirmMessage', { name: sanitizeFileName(detail.video.file_name) }) : ''}
          variant="warning"
          confirmLabel={t('common.reprocess')}
          onConfirm={handleReprocessVideo}
          onCancel={() => setReprocessModalOpen(false)}
        />
      </div>
    </Layout>
  )
}
