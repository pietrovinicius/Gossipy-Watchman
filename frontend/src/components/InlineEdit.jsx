import { useState, useRef, useEffect } from 'react'

export default function InlineEdit({ value, onSave, className = '' }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const inputRef = useRef(null)

  useEffect(() => {
    if (editing) inputRef.current?.focus()
  }, [editing])

  const commit = () => {
    const trimmed = draft.trim()
    if (trimmed && trimmed !== value) onSave(trimmed)
    setEditing(false)
    setDraft(value)
  }

  const cancel = () => {
    setEditing(false)
    setDraft(value)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') commit()
    if (e.key === 'Escape') cancel()
  }

  if (editing) {
    return (
      <input
        ref={inputRef}
        className={className}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={commit}
      />
    )
  }

  return (
    <span
      className={className}
      onClick={() => { setDraft(value); setEditing(true) }}
      style={{ cursor: 'text' }}
      title="Clique para editar"
    >
      {value}
    </span>
  )
}
