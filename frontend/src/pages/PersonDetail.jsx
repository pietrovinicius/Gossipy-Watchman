import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, UserCircle, Pencil, Check, X, AlertCircle } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'
import { sanitizeFileName } from '../utils/sanitizeFileName'

function fmt3(n) {
  return n != null ? Number(n).toFixed(3) : '—'
}

function fmtSec(s) {
  return s != null ? `${Number(s).toFixed(1)}s` : '—'
}

export default function PersonDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [person, setPerson] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [loadErr, setLoadErr] = useState('')
  const [editing, setEditing] = useState(false)
  const [nameInput, setNameInput] = useState('')
  const [nameErr, setNameErr] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    Promise.all([
      api.get(`/people/${id}`),
      api.get(`/people/${id}/timeline`),
    ])
      .then(([pRes, tRes]) => {
        setPerson(pRes.data)
        setNameInput(pRes.data.name)
        setTimeline(tRes.data)
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
          <div className="card flex items-center gap-6">
            {/* Avatar */}
            <div className="w-20 h-20 rounded-2xl overflow-hidden bg-surface border border-border flex-shrink-0">
              {imgSrc ? (
                <img
                  src={imgSrc}
                  alt={`Foto de ${person.name}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <UserCircle className="w-10 h-10 text-text-muted" aria-hidden="true" />
                </div>
              )}
            </div>

            {/* Name + edit */}
            <div className="flex-1 min-w-0">
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
                    <button
                      onClick={saveName}
                      disabled={saving}
                      aria-label="Confirmar nome"
                      className="w-8 h-8 flex items-center justify-center rounded-lg bg-success/20
                                 text-success hover:bg-success/30 transition-colors duration-200 cursor-pointer"
                    >
                      <Check className="w-4 h-4" aria-hidden="true" />
                    </button>
                    <button
                      onClick={() => { setEditing(false); setNameInput(person.name); setNameErr('') }}
                      aria-label="Cancelar edição"
                      className="w-8 h-8 flex items-center justify-center rounded-lg bg-border
                                 text-text-muted hover:text-text-base transition-colors duration-200 cursor-pointer"
                    >
                      <X className="w-4 h-4" aria-hidden="true" />
                    </button>
                  </div>
                  {nameErr && <p className="text-xs text-error-color">{nameErr}</p>}
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold text-text-base truncate">{person.name}</h1>
                  <button
                    onClick={() => setEditing(true)}
                    aria-label="Editar nome"
                    className="text-text-muted hover:text-primary transition-colors duration-200 cursor-pointer flex-shrink-0"
                  >
                    <Pencil className="w-4 h-4" aria-hidden="true" />
                  </button>
                </div>
              )}
              <p className="text-text-muted text-xs mt-1">
                ID #{person.id} · Cadastrado em{' '}
                {new Date(person.created_at).toLocaleDateString('pt-BR')}
              </p>
            </div>
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
