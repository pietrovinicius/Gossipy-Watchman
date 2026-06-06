export default function MergeActionBar({ selected, primaryId, onSetPrimary, onMerge, onCancel }) {
  if (selected.length === 0) return null

  const canMerge = primaryId !== null && selected.length >= 2

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50
                    flex items-center gap-3 px-5 py-3 rounded-2xl
                    bg-card border border-border shadow-2xl shadow-black/40">
      <span className="text-sm text-text-muted">
        {selected.length} selecionado{selected.length !== 1 ? 's' : ''}
      </span>

      {primaryId === null && selected.length >= 1 && (
        <button
          onClick={() => onSetPrimary(selected[0])}
          className="text-xs px-3 py-1.5 rounded-lg bg-surface border border-border
                     text-text-muted hover:text-text-base transition-colors"
        >
          Definir principal
        </button>
      )}

      {primaryId !== null && (
        <span className="text-xs text-primary">Principal: #{primaryId}</span>
      )}

      <button
        onClick={onMerge}
        disabled={!canMerge}
        aria-label="Mesclar perfis selecionados"
        className="text-xs px-4 py-1.5 rounded-lg bg-primary text-bg font-medium
                   disabled:opacity-40 disabled:cursor-not-allowed
                   hover:enabled:opacity-90 transition-opacity"
      >
        Mesclar
      </button>

      <button
        onClick={onCancel}
        aria-label="Cancelar seleção"
        className="text-xs px-3 py-1.5 rounded-lg border border-border
                   text-text-muted hover:text-text-base transition-colors"
      >
        Cancelar
      </button>
    </div>
  )
}
