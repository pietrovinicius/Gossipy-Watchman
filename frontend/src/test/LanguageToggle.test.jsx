import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

const changeLanguageMock = vi.fn()
let mockLanguage = 'en'

vi.mock('react-i18next', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    useTranslation: () => ({
      i18n: {
        get language() {
          return mockLanguage
        },
        changeLanguage: changeLanguageMock,
      },
      t: (key) => key,
    }),
  }
})

import { LanguageToggle } from '../components/LanguageToggle'

describe('LanguageToggle', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLanguage = 'en'
  })

  it('exibe bandeira 🇧🇷 quando idioma atual é inglês', () => {
    mockLanguage = 'en'
    render(<LanguageToggle />)

    expect(screen.getByText('🇧🇷')).toBeInTheDocument()
  })

  it('exibe bandeira 🇺🇸 quando idioma atual é português', () => {
    mockLanguage = 'pt-BR'
    render(<LanguageToggle />)

    expect(screen.getByText('🇺🇸')).toBeInTheDocument()
  })

  it('clicar no botão chama i18n.changeLanguage com o idioma correto (en → pt-BR)', () => {
    mockLanguage = 'en'
    render(<LanguageToggle />)

    fireEvent.click(screen.getByRole('button'))

    expect(changeLanguageMock).toHaveBeenCalledWith('pt-BR')
  })

  it('clicar no botão alterna de pt-BR para en', () => {
    mockLanguage = 'pt-BR'
    render(<LanguageToggle />)

    fireEvent.click(screen.getByRole('button'))

    expect(changeLanguageMock).toHaveBeenCalledWith('en')
  })

  it('persiste preferência em localStorage via i18next-browser-languagedetector (chave gw-language)', async () => {
    const i18n = (await import('../i18n/index.js')).default
    await i18n.changeLanguage('pt-BR')

    expect(localStorage.getItem('gw-language')).toBe('pt-BR')

    await i18n.changeLanguage('en')
  })
})
