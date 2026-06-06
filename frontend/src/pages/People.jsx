import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, UserCircle, ChevronRight, GitMerge, ScanFace, X, Loader2, Link } from 'lucide-react'
import Layout from '../components/Layout'
import InlineEdit from '../components/InlineEdit'
import CategoryBadge from '../components/CategoryBadge'
import MergeActionBar from '../components/MergeActionBar'
import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'
import { useFaceSearch } from '../hooks/useFaceSearch.js'

function PersonCard({ person, onRename, onClick, selectable, selected, onToggleSelect }) {
  const filename = person.profile_image_path
    ? person.profile_image_path.split('/').pop()
    : null
  const imgSrc = useAuthImage(filename)

  const created = new Date(person.created_at).toLocaleDateString('pt-BR')

  return (
    <div
      className={`card text-left hover:border-primary/50 hover:bg-surface/80
                 transition-all duration-200 group w-full relative
                 ${selected ? 'border-primary ring-1 ring-primary/40' : ''}`}
    >
      {selectable && (
        <button
          onClick={() => onToggleSelect(person.id)}
          aria-label={selected ? `Desmarcar ${person.name}` : `Selecionar ${person.name}`}
          className={`absolute top-2 right-2 w-5 h-5 rounded border-2 transition-colors
                      ${selected
                        ? 'bg-primary border-primary'
                        : 'bg-transparent border-border hover:border-primary'}`}
        />
      )}

      <div className="flex items-center gap-3">
        {/* Avatar — clica para navegar */}
        <button
          onClick={selectable ? () => onToggleSelect(person.id) : onClick}
          className="w-14 h-14 rounded-xl overflow-hidden bg-surface flex-shrink-0 border border-border
                     focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          aria-label={`Ver detalhes de ${person.name}`}
        >
          {imgSrc ? (
            <img src={imgSrc} alt={`Foto de ${person.name}`} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <UserCircle className="w-8 h-8 text-text-muted" aria-hidden="true" />
            </div>
          )}
        </button>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <InlineEdit
            value={person.name}
            onSave={(newName) => onRename(person.id, newName)}
            className="text-text-base font-medium text-sm truncate group-hover:text-primary
                       transition-colors duration-200 bg-transparent border-none outline-none w-full"
          />
          <div className="flex items-center gap-2 mt-0.5">
            <p className="text-text-muted text-xs">Cadastrado em {created}</p>
            <CategoryBadge category={person.category} />
          </div>
        </div>

        {!selectable && (
          <button
            onClick={onClick}
            className="focus-visible:ring-2 focus-visible:ring-primary rounded p-0.5"
            aria-label={`Ver detalhes de ${person.name}`}
          >
            <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-primary flex-shrink-0
                                      transition-colors duration-200" aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  )
}

export default function People() {
  const navigate = useNavigate()
  const [people, setPeople] = useState(null)
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')

  // face search
  const { results: faceResults, loading: faceLoading, error: faceError, queryTimeMs, search: faceSearch, reset: faceReset } = useFaceSearch()
  const [faceSearchOpen, setFaceSearchOpen] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) faceSearch(file)
  }

  function handleFileSelect(e) {
    const file = e.target.files[0]
    if (file) faceSearch(file)
  }

  // merge state
  const [mergeMode, setMergeMode] = useState(false)
  const [selected, setSelected] = useState([])
  const [primaryId, setPrimaryId] = useState(null)
  const [merging, setMerging] = useState(false)

  useEffect(() => {
    api.get('/people?limit=200')
      .then((r) => setPeople(r.data))
      .catch((err) => setError(err.message))
  }, [])

  const handleRename = async (id, newName) => {
    try {
      const res = await api.patch(`/people/${id}`, { name: newName })
      setPeople((prev) => prev.map((p) => p.id === id ? { ...p, name: res.data.name } : p))
    } catch {
      // cancela silenciosamente — InlineEdit restaura valor anterior
    }
  }

  const toggleSelect = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )
  }

  const cancelMerge = () => {
    setMergeMode(false)
    setSelected([])
    setPrimaryId(null)
  }

  const handleMerge = async () => {
    if (!primaryId || selected.length < 2) return
    const secondaryIds = selected.filter((id) => id !== primaryId)
    setMerging(true)
    try {
      await api.post('/people/merge', { primary_id: primaryId, secondary_ids: secondaryIds })
      const res = await api.get('/people?limit=200')
      setPeople(res.data)
      cancelMerge()
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message)
    } finally {
      setMerging(false)
    }
  }

  const filtered = people?.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  ) ?? []

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6 pb-24">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl font-bold text-text-base">Pessoas</h1>
          <div className="flex items-center gap-3">
            {people && (
              <p className="text-text-muted text-sm">
                {filtered.length} de {people.length} pessoa{people.length !== 1 ? 's' : ''}
              </p>
            )}
            {people && people.length >= 2 && (
              <button
                onClick={() => setMergeMode((m) => !m)}
                className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border
                            transition-colors ${mergeMode
                              ? 'bg-primary/10 border-primary text-primary'
                              : 'border-border text-text-muted hover:text-text-base'}`}
              >
                <GitMerge className="w-3.5 h-3.5" aria-hidden="true" />
                {mergeMode ? 'Modo mescla ativo' : 'Mesclar perfis'}
              </button>
            )}
          </div>
        </div>

        {/* Face Search Panel */}
        <div>
          <button
            onClick={() => { setFaceSearchOpen((o) => !o); faceReset() }}
            className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border border-border
                       text-text-muted hover:text-text-base hover:border-primary/50 transition-colors cursor-pointer"
            aria-expanded={faceSearchOpen}
          >
            <ScanFace className="w-4 h-4" aria-hidden="true" />
            Buscar por face
          </button>

          {faceSearchOpen && (
            <div className="mt-3 border border-border rounded-xl p-4 bg-surface space-y-3">
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                aria-label="Área de upload para busca por face"
                className={`flex flex-col items-center justify-center gap-2 py-8 rounded-lg border-2 border-dashed
                            cursor-pointer transition-colors
                            ${dragOver ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/50'}`}
              >
                {faceLoading
                  ? <Loader2 className="w-8 h-8 text-primary animate-spin" aria-hidden="true" />
                  : <ScanFace className="w-8 h-8 text-text-muted" aria-hidden="true" />
                }
                <p className="text-sm text-text-muted">
                  {faceLoading ? 'Buscando…' : 'Arraste uma imagem ou clique para selecionar'}
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png"
                className="hidden"
                onChange={handleFileSelect}
                aria-label="Selecionar imagem para busca por face"
              />

              {faceError && (
                <p role="alert" className="text-error-color text-xs">{faceError}</p>
              )}

              {faceResults.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs text-text-muted">
                    {faceResults.length} resultado{faceResults.length !== 1 ? 's' : ''}
                    {queryTimeMs !== null && ` — ${queryTimeMs}ms`}
                  </p>
                  {faceResults.map((r) => (
                    <div key={r.person_id} className="flex items-center justify-between text-sm
                                                       bg-card rounded-lg px-3 py-2">
                      <span className="font-medium text-text-base">{r.person_name}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-text-muted">{r.confidence_pct}% confiança</span>
                        <button
                          onClick={() => navigate(`/people/${r.person_id}`)}
                          className="text-primary hover:underline text-xs flex items-center gap-1 cursor-pointer"
                          aria-label={`Ver perfil de ${r.person_name}`}
                        >
                          <Link className="w-3 h-3" aria-hidden="true" />
                          Ver perfil
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {!faceLoading && faceResults.length === 0 && !faceError && (
                <p className="text-xs text-text-muted text-center">
                  Nenhum resultado ainda. Envie uma imagem com face visível.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" aria-hidden="true" />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nome…"
            aria-label="Buscar pessoa por nome"
            className="w-full bg-surface border border-border rounded-lg pl-9 pr-4 py-2.5 text-sm
                       text-text-base placeholder-text-muted focus:outline-none focus:ring-2
                       focus:ring-primary focus:border-transparent transition-colors duration-200"
          />
        </div>

        {mergeMode && (
          <p className="text-xs text-text-muted bg-surface border border-border rounded-lg px-3 py-2">
            Selecione 2 ou mais perfis. Depois defina qual é o perfil principal antes de mesclar.
          </p>
        )}

        {error && (
          <p role="alert" className="text-error-color text-sm">{error}</p>
        )}

        {/* Grid */}
        {people === null ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }, (_, i) => (
              <div key={i} className="card h-20 animate-pulse bg-card/50" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-text-muted">
            <UserCircle className="w-12 h-12 mx-auto mb-3 opacity-40" aria-hidden="true" />
            <p className="text-sm">
              {search ? 'Nenhuma pessoa encontrada para esta busca.' : 'Nenhuma pessoa catalogada ainda.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((p) => (
              <PersonCard
                key={p.id}
                person={p}
                onRename={handleRename}
                onClick={() => navigate(`/people/${p.id}`)}
                selectable={mergeMode}
                selected={selected.includes(p.id)}
                onToggleSelect={toggleSelect}
              />
            ))}
          </div>
        )}
      </div>

      <MergeActionBar
        selected={selected}
        primaryId={primaryId}
        onSetPrimary={(id) => setPrimaryId(id)}
        onMerge={handleMerge}
        onCancel={cancelMerge}
      />
    </Layout>
  )
}
