import { render, screen, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ThemeProvider, useTheme } from '../contexts/ThemeContext'

function Probe() {
  const { theme, toggleTheme } = useTheme()
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <button onClick={toggleTheme}>toggle</button>
    </div>
  )
}

function renderProbe() {
  return render(
    <ThemeProvider>
      <Probe />
    </ThemeProvider>
  )
}

describe('ThemeContext', () => {
  let matchMediaSpy

  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.classList.remove('dark', 'light')
    matchMediaSpy = vi.fn()
    window.matchMedia = matchMediaSpy
  })

  it('lê tema salvo no localStorage quando disponível', () => {
    window.localStorage.setItem('gw-theme', 'light')
    matchMediaSpy.mockReturnValue({ matches: true })

    renderProbe()

    expect(screen.getByTestId('theme-value').textContent).toBe('light')
  })

  it('usa "dark" quando localStorage vazio e sistema prefere dark', () => {
    matchMediaSpy.mockReturnValue({ matches: true })

    renderProbe()

    expect(screen.getByTestId('theme-value').textContent).toBe('dark')
  })

  it('usa "light" quando localStorage vazio e sistema não prefere dark', () => {
    matchMediaSpy.mockReturnValue({ matches: false })

    renderProbe()

    expect(screen.getByTestId('theme-value').textContent).toBe('light')
  })

  it('toggleTheme alterna entre dark e light', () => {
    window.localStorage.setItem('gw-theme', 'dark')
    matchMediaSpy.mockReturnValue({ matches: false })

    renderProbe()
    expect(screen.getByTestId('theme-value').textContent).toBe('dark')

    act(() => { screen.getByText('toggle').click() })
    expect(screen.getByTestId('theme-value').textContent).toBe('light')

    act(() => { screen.getByText('toggle').click() })
    expect(screen.getByTestId('theme-value').textContent).toBe('dark')
  })

  it('persiste o novo tema no localStorage ao alternar', () => {
    window.localStorage.setItem('gw-theme', 'dark')
    matchMediaSpy.mockReturnValue({ matches: false })

    renderProbe()
    act(() => { screen.getByText('toggle').click() })

    expect(window.localStorage.getItem('gw-theme')).toBe('light')
  })

  it('aplica classe "dark" ao documentElement quando tema=dark', () => {
    window.localStorage.setItem('gw-theme', 'dark')
    matchMediaSpy.mockReturnValue({ matches: false })

    renderProbe()

    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(document.documentElement.classList.contains('light')).toBe(false)
  })

  it('aplica classe "light" ao documentElement quando tema=light', () => {
    window.localStorage.setItem('gw-theme', 'light')
    matchMediaSpy.mockReturnValue({ matches: false })

    renderProbe()

    expect(document.documentElement.classList.contains('light')).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
})
