import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, UserCircle, Pencil, Check, X, AlertCircle } from 'lucide-react'
import Layout from '../components/Layout'
import CategoryBadge from '../components/CategoryBadge'
import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'
import { sanitizeFileName } from '../utils/sanitizeFileName'

const CATEGORIES = ['Funcionário', 'Visitante', 'Desconhecido', 'Monitorado']

function fmt3(n) {
  return n != null ? Number(n).toFixed(3) : '—'
}

function fmtSec(s) {
  return s != null ? `${Number(s).toFixed(1)}s` : '—'
}

function fmtDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export default function PersonDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [person, setPerson] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [stats, setStats] = useState(null)
  const [loadErr, setLoadErr] = useState('')

  // name edit state
  const [editing, setEditing] = useState(false)
  const [nameInput, setNameInput] = useState('')
  const [nameErr, setNameErr] = useState('')
  const [saving, setSaving] = useState(false)

  // meta edit state (notes + category)
  const [editingMeta, setEditingMeta] = useState(false)
  const [notesInput, setNotesInput] = useState('')
  const [categoryInput, setCategoryInput] = useState('Desconhecido')
  const [metaErr, setMetaErr] = useState('')
  const [savingMeta, setSavingMeta] = useState(false)

  useEffect(() => {
    Promise.all([
      api.get(`/people/${id}`),
      api.get(`/people/${id}/timeline`),
      api.get(`/people/${id}/stats`),
    ])
      .then(([pRes, tRes, sRes]) => {
        setPerson(pRes.data)
        setNameInput(pRes.data.name)
        setNotesInput(pRes.data.notes ?? '')
        setCategoryInput(pRes.data.category ?? 'Desconhecido')
        setTimeline(tRes.data)
        setStats(sRes.data)
      })
      .catch((err) => setLoadErr(err.message))
  }, [id])

  async function saveName() {
    if (!nameInput.trim()) { setNameErr('Nome não pode ser vazio.'); return }
    setSaving(true)
    setNameErr('')
    try {
      const res = await api.patch(`/people/${id}`, { name: nameInput.trim() })
      setPerson(res.data)
      setEditing(false)
    } catch (err) {
      setNameErr(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function saveMeta() {
    setSavingMeta(true)
    setMetaErr('')
    try {
      const payload = {}
      if (notesInput !== (person.notes ?? '')) payload.notes = notesInput
      if (categoryInput !== person.category) payload.category = categoryInput
      if (Object.keys(payload).length === 0) { setEditingMeta(false); setSavingMeta(false); return }
      const res = await api.patch(`/people/${id}`, payload)
      setPerson(res.data)
      setEditingMeta(false)
    } catch (err) {
      setMetaErr(err.message)
    } finally {
      setSavingMeta(false)
    }
  }

  if (loadErr) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center py-24 gap-4 text-error-color">
          <AlertCircle className="w-10 h-10" aria-hidden="true" />
          <p className="text-sm">{loadErr}</p>
          <button onClick={() => navigate('/people')} className="btn-primary text-sm">
            Voltar para Pessoas
          </button>
        </div>
      </Layout>
    )
  }

  const filename = person?.profile_image_path
    ? person.profile_image_path.split('/').pop()
    : null
  const imgSrc = useAuthImage(filename)

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Back */}
        <button
          onClick={() => navigate('/people')}
          className="flex items-center gap-2 text-text-muted hover:text-text-base
                     transition-colors duration-200 cursor-pointer text-sm"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          Voltar para Pessoas
        </button>

        {/* Profile */}
        {person === null ? (
          <div className="card h-32 animate-pulse" />
        ) : (
          <div className="card flex items-start gap-6">
            {/* Avatar */}
            <div className="w-20 h-20 rounded-2xl overflow-hidden bg-surface border border-border flex-shrink-0">
              {imgSrc ? (
                <img src={imgSrc} alt={`Foto de ${person.name}`} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <UserCircle className="w-10 h-10 text-text-muted" aria-hidden="true" />
                </div>
              )}
            </div>

            {/* Name + meta */}
            <div className="flex-1 min-w-0 space-y-3">
              {/* Name row */}
              {editing ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={nameInput}
                      onChange={(e) => setNameInput(e.target.value)}
                      onKeyDown={(e) => { if (e.key === 'Enter') saveName(); if (e.key === 'Escape') setEditing(false) }}
                      autoFocus
                      aria-label="Nome da pessoa"
                      className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm
                                 text-text-base focus:outline-none focus:ring-2 focus:ring-primary
                                 focus:border-transparent transition-colors duration-200"
                    />
                    <button onClick={saveName} disabled={saving} aria-label="Confirmar nome"
                      className="w-8 h-8 flex items-center justify-center rounded-lg bg-success/20
                                 text-success hover:bg-success/30 transition-colors duration-200 cursor-pointer">
                      <Check className="w-4 h-4" aria-hidden="true" />
                    </button>
                    <button onClick={() => { setEditing(false); setNameInput(person.name); setNameErr('') }}
                      aria-label="Cancelar edição"
                      className="w-8 h-8 flex items-center justify-center rounded-lg bg-border
                                 text-text-muted hover:text-text-base transition-colors duration-200 cursor-pointer">
                      <X className="w-4 h-4" aria-hidden="true" />
                    </button>
                  </div>
                  {nameErr && <p className="text-xs text-error-color">{nameErr}</p>}
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold text-text-base truncate">{person.name}</h1>
                  <button onClick={() => setEditing(true)} aria-label="Editar nome"
                    className="text-text-muted hover:text-primary transition-colors duration-200 cursor-pointer flex-shrink-0">
                    <Pencil className="w-4 h-4" aria-hidden="true" />
                  </button>
                </div>
              )}

              <p className="text-text-muted text-xs">
                ID #{person.id} · Cadastrado em{' '}
                {new Date(person.created_at).toLocaleDateString('pt-BR')}
              </p>

              {/* Category + notes */}
              {editingMeta ? (
                <div className="space-y-2 pt-1">
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-text-muted w-20 flex-shrink-0">Categoria</label>
                    <select
                      value={categoryInput}
                      onChange={(e) => setCategoryInput(e.target.value)}
                      className="flex-1 bg-surface border border-border rounded-lg px-2 py-1.5 text-sm
                                 text-text-base focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                  <div className="flex items-start gap-2">
                    <label className="text-xs text-text-muted w-20 flex-shrink-0 pt-1.5">Notas</label>
                    <textarea
                      value={notesInput}
                      onChange={(e) => setNotesInput(e.target.value)}
                      rows={3}
                      placeholder="Observações sobre esta pessoa…"
                      className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm
                                 text-text-base focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button onClick={saveMeta} disabled={savingMeta}
                      className="btn-primary text-xs px-3 py-1.5">
                      {savingMeta ? 'Salvando…' : 'Salvar'}
                    </button>
                    <button onClick={() => { setEditingMeta(false); setMetaErr('') }}
                      className="text-xs px-3 py-1.5 border border-border rounded-lg text-text-muted hover:text-text-base">
                      Cancelar
                    </button>
                  </div>
                  {metaErr && <p className="text-xs text-error-color">{metaErr}</p>}
                </div>
              ) : (
                <div className="flex items-start gap-3">
                  <CategoryBadge category={person.category} />
                  {person.notes && (
                    <p className="text-xs text-text-muted italic">{person.notes}</p>
                  )}
                  <button onClick={() => setEditingMeta(true)} aria-label="Editar categoria e notas"
                    className="text-text-muted hover:text-primary transition-colors duration-200 cursor-pointer flex-shrink-0 ml-auto">
                    <Pencil className="w-3.5 h-3.5" aria-hidden="true" />
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'Vídeos', value: stats.video_count },
              { label: 'Tempo total', value: `${stats.total_seconds.toFixed(1)}s` },
              { label: 'Primeira vez', value: fmtDate(stats.first_seen) },
              { label: 'Última vez', value: fmtDate(stats.last_seen) },
            ].map(({ label, value }) => (
              <div key={label} className="card py-3 text-center">
                <p className="text-xs text-text-muted mb-1">{label}</p>
                <p className="text-base font-semibold text-text-base">{value}</p>
              </div>
            ))}
          </div>
        )}

        {/* Timeline */}
        <div className="card p-0 overflow-hidden">
          <div className="px-4 py-3 border-b border-border">
            <h2 className="text-sm font-semibold text-text-base">Timeline de aparições</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Vídeo</th>
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Início</th>
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Fim</th>
                  <th className="text-left px-4 py-2.5 text-text-muted font-medium">Confiança</th>
                </tr>
              </thead>
              <tbody>
                {timeline === null ? (
                  Array.from({ length: 3 }, (_, i) => (
                    <tr key={i}>
                      {[1, 2, 3, 4].map((k) => (
                        <td key={k} className="px-4 py-3">
                          <div className="h-4 bg-border rounded animate-pulse" />
                        </td>
                      ))}
                    </tr>
                  ))
                ) : timeline.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-text-muted text-sm">
                      Nenhuma aparição registrada.
                    </td>
                  </tr>
                ) : (
                  timeline.map((a) => (
                    <tr key={a.id} className="border-b border-border/50 hover:bg-surface/60 transition-colors duration-150">
                      <td className="px-4 py-3 font-mono text-xs text-text-base truncate max-w-[180px]">{sanitizeFileName(a.file_name)}</td>
                      <td className="px-4 py-3 text-text-muted font-mono text-xs">{fmtSec(a.timestamp_start)}</td>
                      <td className="px-4 py-3 text-text-muted font-mono text-xs">{fmtSec(a.timestamp_end)}</td>
                      <td className="px-4 py-3 text-text-muted font-mono text-xs">{fmt3(a.confidence)}</td>
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
