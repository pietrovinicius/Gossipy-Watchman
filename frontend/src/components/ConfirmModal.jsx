import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'

const VARIANT_BUTTON_CLASSES = {
  danger: 'bg-red-600 hover:bg-red-700 focus-visible:ring-red-600',
  warning: 'bg-yellow-600 hover:bg-yellow-700 focus-visible:ring-yellow-600',
  info: 'bg-blue-600 hover:bg-blue-700 focus-visible:ring-blue-600',
}

/**
 * @param {{
 *   isOpen: boolean,
 *   title: string,
 *   message: string,
 *   confirmLabel?: string,
 *   cancelLabel?: string,
 *   variant?: 'danger' | 'warning' | 'info',
 *   onConfirm: () => void,
 *   onCancel: () => void,
 *   requireTyping?: boolean,
 *   confirmWord?: string,
 * }} props
 */
export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmLabel,
  cancelLabel,
  variant = 'danger',
  onConfirm,
  onCancel,
  requireTyping = false,
  confirmWord = '',
}) {
  const { t } = useTranslation()
  const [typedValue, setTypedValue] = useState('')

  useEffect(() => {
    if (!isOpen) return

    setTypedValue('')

    function handleKeyDown(e) {
      if (e.key === 'Escape') onCancel()
    }

    document.addEventListener('keydown', handleKeyDown)
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [isOpen, onCancel])

  if (!isOpen) return null

  const buttonVariantClass = VARIANT_BUTTON_CLASSES[variant] ?? VARIANT_BUTTON_CLASSES.danger
  const isConfirmDisabled = requireTyping && typedValue !== confirmWord

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onClick={onCancel}
      className="fixed inset-0 z-50 flex items-center justify-center
                 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md rounded-2xl bg-white dark:bg-neutral-900 p-6 shadow-2xl
                   animate-in zoom-in-95 duration-200"
      >
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">{title}</h2>
        <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-300">{message}</p>

        {requireTyping && (
          <input
            type="text"
            value={typedValue}
            onChange={(e) => setTypedValue(e.target.value)}
            placeholder={t('confirmModal.typeToConfirm', { word: confirmWord })}
            className="mt-4 w-full rounded-lg border border-neutral-300 dark:border-neutral-700
                       bg-transparent px-3 py-2 text-sm text-neutral-900 dark:text-neutral-50
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          />
        )}

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="rounded-lg px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-200
                       hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors duration-200
                       cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            {cancelLabel ?? t('confirmModal.cancel')}
          </button>
          <button
            onClick={onConfirm}
            disabled={isConfirmDisabled}
            className={`rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors duration-200
                        cursor-pointer focus-visible:outline-none focus-visible:ring-2
                        disabled:opacity-50 disabled:cursor-not-allowed ${buttonVariantClass}`}
          >
            {confirmLabel ?? t('confirmModal.confirm')}
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}
