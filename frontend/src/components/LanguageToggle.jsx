import { useLanguage } from '../hooks/useLanguage'

export function LanguageToggle({ collapsed = false }) {
  const { isEnglish, toggle } = useLanguage()

  return (
    <button
      onClick={toggle}
      title={isEnglish ? 'Mudar para Português' : 'Switch to English'}
      aria-label={isEnglish ? 'Switch to Portuguese' : 'Switch to English'}
      className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium
                 text-text-muted hover:bg-card hover:text-text-base
                 transition-colors duration-200 cursor-pointer
                 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
    >
      <span className="text-base leading-none flex-shrink-0" aria-hidden="true">
        {isEnglish ? '🇧🇷' : '🇺🇸'}
      </span>
      {!collapsed && (
        <span className="flex-1 text-left">
          {isEnglish ? 'Português' : 'English'}
        </span>
      )}
    </button>
  )
}
