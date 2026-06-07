const TZ_DESIGNATOR = /[zZ]|[+-]\d{2}:?\d{2}$/

/**
 * Backend serializa datetimes naive em UTC (ex.: "2026-06-07T12:00:02").
 * Sem designador de timezone, `new Date()` interpreta a string como horário
 * local, deslocando a hora exibida. Aqui forçamos a leitura como UTC.
 */
export function parseUtcDate(dateStr) {
  if (!dateStr) return null
  const iso = TZ_DESIGNATOR.test(dateStr) ? dateStr : `${dateStr}Z`
  return new Date(iso)
}

export function formatDateTime(dateStr) {
  const date = parseUtcDate(dateStr)
  if (!date) return ''
  return date.toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}
