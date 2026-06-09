import { useTranslation } from 'react-i18next'

export function useLanguage() {
  const { i18n } = useTranslation()

  const currentLanguage = i18n.language
  const isEnglish = currentLanguage === 'en'
  const isPortuguese = currentLanguage === 'pt-BR'

  const setEnglish = () => i18n.changeLanguage('en')
  const setPortuguese = () => i18n.changeLanguage('pt-BR')
  const toggle = () => (isEnglish ? setPortuguese() : setEnglish())

  return {
    currentLanguage,
    isEnglish,
    isPortuguese,
    setEnglish,
    setPortuguese,
    toggle,
  }
}
