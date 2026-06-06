import { useState, useEffect, useCallback } from 'react'
import { Bell, CheckCheck, AlertTriangle, Clock, Video } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../services/api'
import { useGlobalWebSocket } from '../hooks/useGlobalWebSocket.js'

function AlertRow({ alert, onMarkSeen }) {
  return (
    <div
      data-seen={String(alert.seen)}
      className={`flex items-start gap-4 p-4 rounded-xl border transition-colors
        ${alert.seen
          ? 'border-border bg-surface opacity-60'
          : 'border-primary/40 bg-primary/5'
        }`}
    >
      <div className={`mt-0.5 rounded-full p-2 flex-shrink-0
        ${alert.seen ? 'bg-border text-text-muted' : 'bg-primary/20 text-primary'}`}>
        <AlertTriangle className="w-4 h-4" aria-hidden="true" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-text-base">{alert.person_name}</p>
        <p className="text-xs text-text-muted mt-0.5">{alert.message}</p>
        <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
          <span className="flex items-center gap-1">
            <Video className="w-3 h-3" aria-hidden="true" />
            {alert.video_file_name}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" aria-hidden="true" />
            {alert.timestamp_in_video.toFixed(1)}s
          </span>
        </div>
      </div>

      <div className="flex-shrink-0 text-right">
        <p className="text-xs text-text-muted">
          {new Date(alert.created_at).toLocaleString('pt-BR')}
        </p>
        {!alert.seen && (
          <button
            aria-label="Marcar como visto"
            onClick={() => onMarkSeen(alert.id)}
            className="mt-2 flex items-center gap-1 text-xs text-primary hover:text-primary/80 cursor-pointer"
          >
            <CheckCheck className="w-3 h-3" aria-hidden="true" />
            Marcar como visto
          </button>
        )}
      </div>
    </div>
  )
}

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState(null)

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await api.get('/alerts')
      setAlerts(res.data)
    } catch {
      // silent — erros de rede não devem crashar a página
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAlerts()
  }, [fetchAlerts])

  useGlobalWebSocket({
    onEvent: (payload) => {
      if (payload.event === 'watchlist_alert') {
        setToast(payload.message)
        setTimeout(() => setToast(null), 5000)
        fetchAlerts()
      }
    },
  })

  async function handleMarkSeen(alertId) {
    try {
      await api.patch('/alerts/seen', { alert_ids: [alertId] })
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, seen: true } : a))
      )
    } catch {
      // no-op
    }
  }

  return (
    <Layout>
      {/* Toast WebSocket */}
      {toast && (
        <div
          role="alert"
          className="fixed top-4 right-4 z-50 bg-primary text-white text-sm px-4 py-3 rounded-xl shadow-lg flex items-center gap-2"
        >
          <AlertTriangle className="w-4 h-4" aria-hidden="true" />
          {toast}
        </div>
      )}

      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Bell className="w-6 h-6 text-primary" aria-hidden="true" />
          <h1 className="text-xl font-bold text-text-base">Alertas de Watchlist</h1>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <div role="status" aria-label="Carregando alertas"
                 className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && alerts.length === 0 && (
          <div className="text-center py-16 text-text-muted">
            <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" aria-hidden="true" />
            <p>Nenhum alerta registrado.</p>
          </div>
        )}

        {!loading && alerts.length > 0 && (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <AlertRow key={alert.id} alert={alert} onMarkSeen={handleMarkSeen} />
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
