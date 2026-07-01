import { useRouteError } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { AlertTriangle } from 'lucide-react'

export default function RouteError() {
  const { t } = useTranslation()
  const error = useRouteError()

  if (import.meta.env.DEV) {
    console.error('Route error boundary:', error)
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-bg px-4">
      <div className="card max-w-md text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-error-color mx-auto" aria-hidden="true" />
        <h1 className="text-lg font-semibold text-text-base">{t('errors.unexpectedTitle')}</h1>
        <p className="text-sm text-text-muted">{t('errors.unexpectedBody')}</p>
        <button onClick={() => window.location.reload()} className="btn-primary">
          {t('common.tryAgain')}
        </button>
      </div>
    </div>
  )
}
