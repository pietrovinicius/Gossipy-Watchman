import { useEffect, useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Film, Clock, Users, UserX, RefreshCw, Download, Loader2, ChevronRight, Eye, Trash2, RotateCcw, RotateCw } from 'lucide-react'
import Layout from '../components/Layout'
import ConfirmModal from '../components/ConfirmModal'
import api from '../services/api'
import { sanitizeFileName } from '../utils/sanitizeFileName'
import { downloadCsv } from '../utils/downloadCsv'
import { formatDateTime } from '../utils/formatDate'
import { useGlobalWebSocket } from '../hooks/useGlobalWebSocket'

const STATUS_BADGE = {
  Pendente:    { cls: 'bg-warning/20 text-warning',       label: 'Pendente' },
  Processando: { cls: 'bg-processing/20 text-processing', label: 'Processando' },
  Concluído:   { cls: 'bg-success/20 text-success',       label: 'Concluído' },
  Erro:        { cls: 'bg-error-color/20 text-error-color', label: 'Erro' },
}

function StatusBadge({ status }) {
  const cfg = STATUS_BADGE[status] ?? { cls: 'bg-border text-text-muted', label: status }
  return <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
}

function MetricCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
        <Icon className="w-6 h-6" aria-hidden="true" />
      </div>
      <div>
        <p className="text-text-muted text-sm">{label}</p>
        <p className="text-2xl font-bold font-mono text-text-base">
          {value ?? <span className="inline-block w-8 h-6 bg-border rounded animate-pulse" />}
        </p>
      </div>
    </div>
  )
}

const STATUS_FILTERS = ['Todos', 'Pendente', 'Processando', 'Concluído', 'Erro']
const REPROCESSABLE_STATUSES = ['Concluído', 'Erro']

function SkeletonRow() {
  return (
    <tr>
      {[1, 2, 3].map((k) => (
        <td key={k} className="px-4 py-3">
          <div className="h-4 bg-border rounded animate-pulse" />
        </td>
      ))}
    </tr>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [videos, setVideos] = useState(null)
  const [people, setPeople] = useState(null)
  const [error, setError] = useState('')
  const [lastRefresh, setLastRefresh] = useState(null)
  const [exportingId, setExportingId] = useState(null)
  const [wsConnected, setWsConnected] = useState(false)
  const [statusFilter, setStatusFilter] = useState('Todos')
  const [showDeleted, setShowDeleted] = useState(false)
  const [videoToDelete, setVideoToDelete] = useState(null)
  const [videoToReprocess, setVideoToReprocess] = useState(null)
  const fetchRef = useRef(null)

  async function handleExportVideo(videoId, fileName) {
    setExportingId(videoId)
    try {
      const res = await api.get(`/export/timeline/video/${videoId}`, { responseType: 'blob' })
      downloadCsv(res.data, `gossipy_video_${videoId}_${sanitizeFileName(fileName)}.csv`)
    } catch {
      // silencia — sem toast ainda
    } finally {
      setExportingId(null)
    }
  }

  const fetchData = useCallback(async () => {
    setError('')
    try {
      let videosUrl = '/videos?limit=200'
      if (statusFilter !== 'Todos') videosUrl += `&status=${encodeURIComponent(statusFilter)}`
      if (showDeleted) videosUrl += '&include_deleted=true'

      const [vRes, pRes] = await Promise.all([
        api.get(videosUrl),
        api.get('/people?limit=200'),
      ])
      setVideos(vRes.data)
      setPeople(pRes.data)
      setLastRefresh(new Date())
    } catch (err) {
      setError(err.message)
    }
  }, [statusFilter, showDeleted])

  // mantém ref atualizada para uso no callback WS sem re-criar o hook
  fetchRef.current = fetchData

  const handleDeleteVideo = async (video) => {
    try {
      await api.delete(`/videos/${video.id}`)
      setVideoToDelete(null)
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
      setVideoToDelete(null)
    }
  }

  const handleRestoreVideo = async (video) => {
    try {
      await api.post(`/videos/${video.id}/restore`)
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    }
  }

  const handleReprocessVideo = async (video) => {
    try {
      await api.post(`/videos/${video.id}/reprocess`)
      setVideoToReprocess(null)
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
      setVideoToReprocess(null)
    }
  }

  useGlobalWebSocket({
    onEvent: useCallback((payload) => {
      if (payload.event === 'status') {
        setWsConnected(true)
        fetchRef.current?.()
      }
    }, []),
  })

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 15000)
    return () => clearInterval(interval)
  }, [fetchData])

  const concluded = videos?.filter((v) => v.status === 'Concluído').length ?? null
  const queued    = videos?.filter((v) => ['Pendente', 'Processando'].includes(v.status)).length ?? null
  const totalPpl  = people?.length ?? null
  const unknown   = people?.filter((p) => p.name.startsWith('Desconhecido')).length ?? null
  const recent    = videos?.slice(0, 10) ?? []

  const fmt = formatDateTime

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-base">Dashboard</h1>
            {lastRefresh && (
              <p className="text-xs text-text-muted mt-0.5">
                Atualizado às {lastRefresh.toLocaleTimeString('pt-BR')} · auto-refresh 15s
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span
              title={wsConnected ? 'Tempo real ativo' : 'WebSocket desconectado'}
              className={`w-2 h-2 rounded-full flex-shrink-0 transition-colors duration-500 ${
                wsConnected ? 'bg-success shadow-[0_0_6px_rgba(0,200,80,0.6)]' : 'bg-border'
              }`}
              aria-label={wsConnected ? 'Tempo real ativo' : 'WebSocket desconectado'}
            />
            <button
              onClick={fetchData}
              aria-label="Atualizar dados"
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border
                         text-text-muted hover:text-text-base hover:border-primary/50
                         transition-colors duration-200 cursor-pointer text-sm"
            >
              <RefreshCw className="w-4 h-4" aria-hidden="true" />
              Atualizar
            </button>
          </div>
        </div>

        {/* Filtros */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            {STATUS_FILTERS.map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                aria-pressed={statusFilter === s}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                  statusFilter === s
                    ? 'bg-primary/10 border-primary text-primary'
                    : 'border-border text-text-muted hover:text-text-base'}`}
              >
                {s}
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowDeleted((s) => !s)}
            aria-pressed={showDeleted}
            className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                        transition-colors ${showDeleted
                          ? 'bg-primary/10 border-primary text-primary'
                          : 'border-border text-text-muted hover:text-text-base'}`}
          >
            <Eye className="w-3.5 h-3.5" aria-hidden="true" />
            Mostrar excluídos
          </button>
        </div>

        {error && (
          <div role="alert" className="p-4 rounded-xl bg-red-950/40 border border-red-800/50 text-error-color text-sm">
            API inacessível: {error}
          </div>
        )}

        {/* Metric cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard icon={Film}  label="Vídeos processados" value={concluded} color="bg-success/20 text-success" />
          <MetricCard icon={Clock} label="Na fila"            value={queued}    color="bg-warning/20 text-warning" />
          <MetricCard icon={Users} label="Pessoas catalogadas" value={totalPpl} color="bg-primary/20 text-primary" />
          <MetricCard icon={UserX} label="Desconhecidos"       value={unknown}  color="bg-text-muted/20 text-text-muted" />
        </div>

        {/* Recent videos table */}
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-border">
            <h2 className="text-sm font-semibold text-text-base">Vídeos recentes</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Arquivo</th>
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Status</th>
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Enviado em</th>
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Exportar</th>
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Ações</th>
                  <th className="px-4 py-2.5" aria-hidden="true" />
                </tr>
              </thead>
              <tbody>
                {videos === null ? (
                  Array.from({ length: 5 }, (_, i) => <SkeletonRow key={i} />)
                ) : recent.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                      Nenhum vídeo enviado ainda.
                    </td>
                  </tr>
                ) : (
                  recent.map((v) => {
                    const name = sanitizeFileName(v.file_name)
                    const isDeleted = Boolean(v.deleted_at)
                    const canReprocess = REPROCESSABLE_STATUSES.includes(v.status)
                    return (
                      <tr
                        key={v.id}
                        onClick={() => navigate(`/videos/${v.id}`)}
                        title="Ver detalhes do vídeo"
                        className={`border-b border-border/50 cursor-pointer hover:bg-slate-50
                                   dark:hover:bg-[#1F2937] transition-colors duration-150 ${isDeleted ? 'opacity-50' : ''}`}
                      >
                        <td className="px-4 py-3 font-mono text-xs text-text-base truncate max-w-[220px]">
                          <div className="flex items-center gap-2">
                            {name}
                            {isDeleted && (
                              <span className="text-[10px] font-medium px-2 py-0.5 rounded-full
                                               bg-error-color/20 text-error-color">
                                Excluído
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3"><StatusBadge status={v.status} /></td>
                        <td className="px-4 py-3 text-text-muted">{fmt(v.uploaded_at)}</td>
                        <td className="px-4 py-3">
                          <button
                            onClick={(e) => { e.stopPropagation(); handleExportVideo(v.id, v.file_name) }}
                            disabled={exportingId === v.id}
                            aria-label={`Exportar CSV do vídeo ${name}`}
                            className="text-text-muted hover:text-primary transition-colors disabled:opacity-40"
                          >
                            {exportingId === v.id
                              ? <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                              : <Download className="w-4 h-4" aria-hidden="true" />}
                          </button>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {!isDeleted && canReprocess && (
                              <button
                                onClick={(e) => { e.stopPropagation(); setVideoToReprocess(v) }}
                                aria-label={`Reprocessar vídeo ${name}`}
                                className="text-text-muted hover:text-primary transition-colors"
                              >
                                <RotateCw className="w-4 h-4" aria-hidden="true" />
                              </button>
                            )}
                            {!isDeleted && (
                              <button
                                onClick={(e) => { e.stopPropagation(); setVideoToDelete(v) }}
                                aria-label={`Excluir vídeo ${name}`}
                                className="text-text-muted hover:text-error-color transition-colors"
                              >
                                <Trash2 className="w-4 h-4" aria-hidden="true" />
                              </button>
                            )}
                            {isDeleted && (
                              <button
                                onClick={(e) => { e.stopPropagation(); handleRestoreVideo(v) }}
                                aria-label={`Restaurar vídeo ${name}`}
                                className="text-text-muted hover:text-primary transition-colors"
                              >
                                <RotateCcw className="w-4 h-4" aria-hidden="true" />
                              </button>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <ChevronRight className="w-4 h-4 text-slate-400" aria-hidden="true" />
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <ConfirmModal
        isOpen={videoToDelete !== null}
        title="Excluir vídeo"
        message={videoToDelete ? `Tem certeza que deseja excluir "${sanitizeFileName(videoToDelete.file_name)}"? Esta ação pode ser desfeita restaurando o vídeo.` : ''}
        variant="danger"
        confirmLabel="Excluir"
        onConfirm={() => handleDeleteVideo(videoToDelete)}
        onCancel={() => setVideoToDelete(null)}
      />

      <ConfirmModal
        isOpen={videoToReprocess !== null}
        title="Reprocessar vídeo"
        message={videoToReprocess ? `O status de "${sanitizeFileName(videoToReprocess.file_name)}" voltará para Pendente e o worker de visão computacional será disparado novamente. Aparições anteriores serão substituídas.` : ''}
        variant="warning"
        confirmLabel="Reprocessar"
        onConfirm={() => handleReprocessVideo(videoToReprocess)}
        onCancel={() => setVideoToReprocess(null)}
      />
    </Layout>
  )
}
