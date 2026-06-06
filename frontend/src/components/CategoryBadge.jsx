const CATEGORY_STYLES = {
  'Funcionário':   'badge-funcionario bg-blue-500/15 text-blue-400 border-blue-500/30',
  'Visitante':     'badge-visitante bg-purple-500/15 text-purple-400 border-purple-500/30',
  'Monitorado':    'badge-monitorado bg-red-500/15 text-red-400 border-red-500/30',
  'Desconhecido':  'bg-border/50 text-text-muted border-border',
}

export default function CategoryBadge({ category }) {
  const label = category ?? 'Desconhecido'
  const cls = CATEGORY_STYLES[label] ?? CATEGORY_STYLES['Desconhecido']
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${cls}`}>
      {label}
    </span>
  )
}
