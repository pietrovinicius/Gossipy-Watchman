import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, UserCircle, ChevronRight } from 'lucide-react'
import Layout from '../components/Layout'
import InlineEdit from '../components/InlineEdit'
import api from '../services/api'
import { useAuthImage } from '../hooks/useAuthImage'

function PersonCard({ person, onRename, onClick }) {
  const filename = person.profile_image_path
    ? person.profile_image_path.split('/').pop()
    : null
  const imgSrc = useAuthImage(filename)

  const created = new Date(person.created_at).toLocaleDateString('pt-BR')

  return (
    <div
      className="card text-left hover:border-primary/50 hover:bg-surface/80
                 transition-all duration-200 group w-full"
    >
      <div className="flex items-center gap-3">
        {/* Avatar — clica para navegar */}
        <button
          onClick={onClick}
          className="w-14 h-14 rounded-xl overflow-hidden bg-surface flex-shrink-0 border border-border
                     focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          aria-label={`Ver detalhes de ${person.name}`}
        >
          {imgSrc ? (
            <img
              src={imgSrc}
              alt={`Foto de ${person.name}`}
              className="w-full h-full object-cover"
            />
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
          <p className="text-text-muted text-xs mt-0.5">Cadastrado em {created}</p>
        </div>

        <button
          onClick={onClick}
          className="focus-visible:ring-2 focus-visible:ring-primary rounded p-0.5"
          aria-label={`Ver detalhes de ${person.name}`}
        >
          <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-primary flex-shrink-0
                                    transition-colors duration-200" aria-hidden="true" />
        </button>
      </div>
    </div>
  )
}

export default function People() {
  const navigate = useNavigate()
  const [people, setPeople] = useState(null)
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')

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
      // silencia — nome volta ao original via InlineEdit
    }
  }

  const filtered = people?.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  ) ?? []

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl font-bold text-text-base">Pessoas</h1>
          {people && (
            <p className="text-text-muted text-sm">
              {filtered.length} de {people.length} pessoa{people.length !== 1 ? 's' : ''}
            </p>
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
              />
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
