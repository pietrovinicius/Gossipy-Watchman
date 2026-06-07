import { useEffect } from 'react'
import { createPortal } from 'react-dom'
import { X } from 'lucide-react'

/**
 * @param {{ isOpen: boolean, onClose: () => void, src: string | null, alt: string }} props
 */
export default function PhotoModal({ isOpen, onClose, src, alt }) {
  useEffect(() => {
    if (!isOpen) return

    function handleKeyDown(e) {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleKeyDown)
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-label={alt}
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center
                 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <button
        onClick={onClose}
        aria-label="Fechar"
        className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-full
                   bg-white/10 text-white hover:bg-white/20 transition-colors duration-200 cursor-pointer
                   focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
      >
        <X className="w-5 h-5" aria-hidden="true" />
      </button>

      {src && (
        <img
          src={src}
          alt={alt}
          onClick={(e) => e.stopPropagation()}
          className="max-w-[90vw] max-h-[90vh] rounded-2xl shadow-2xl object-contain
                     animate-in zoom-in-95 duration-200"
        />
      )}
    </div>,
    document.body
  )
}
