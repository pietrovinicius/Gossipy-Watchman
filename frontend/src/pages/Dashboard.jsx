import { useEffect, useState, useCallback } from 'react'
import { Film, Clock, Users, UserX, RefreshCw } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../services/api'

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
  const [videos, setVideos] = useState(null)
  const [people, setPeople] = useState(null)
  const [error, setError] = useState('')
  const [lastRefresh, setLastRefresh] = useState(null)

  const fetchData = useCallback(async () => {
    setError('')
    try {
      const [vRes, pRes] = await Promise.all([
        api.get('/videos?limit=200'),
        api.get('/people?limit=200'),
      ])
      setVideos(vRes.data)
      setPeople(pRes.data)
      setLastRefresh(new Date())
    } catch (err) {
      setError(err.message)
    }
  }, [])

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

  function fmt(dateStr) {
    return new Date(dateStr).toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  }

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
                </tr>
              </thead>
              <tbody>
                {videos === null ? (
                  Array.from({ length: 5 }, (_, i) => <SkeletonRow key={i} />)
                ) : recent.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-4 py-8 text-center text-text-muted">
                      Nenhum vídeo enviado ainda.
                    </td>
                  </tr>
                ) : (
                  recent.map((v) => (
                    <tr key={v.id} className="border-b border-border/50 hover:bg-surface/60 transition-colors duration-150">
                      <td className="px-4 py-3 font-mono text-xs text-text-base truncate max-w-[220px]">{v.file_name}</td>
                      <td className="px-4 py-3"><StatusBadge status={v.status} /></td>
                      <td className="px-4 py-3 text-text-muted">{fmt(v.uploaded_at)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  )
}
