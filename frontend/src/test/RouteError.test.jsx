import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

const useRouteErrorMock = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useRouteError: () => useRouteErrorMock() }
})

describe('RouteError', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useRouteErrorMock.mockReturnValue(new Error('falha simulada'))
  })

  it('exibe mensagem amigável em vez da tela branca do dev overlay', async () => {
    const { default: RouteError } = await import('../components/RouteError.jsx')
    render(<RouteError />)

    expect(screen.getByRole('heading')).toBeTruthy()
    expect(screen.getByRole('button', { name: /try again/i })).toBeTruthy()
  })

  it('botão "Try again" recarrega a página', async () => {
    const reloadMock = vi.fn()
    const originalLocation = window.location
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: { ...originalLocation, reload: reloadMock },
    })

    const { default: RouteError } = await import('../components/RouteError.jsx')
    render(<RouteError />)

    fireEvent.click(screen.getByRole('button', { name: /try again/i }))
    expect(reloadMock).toHaveBeenCalledTimes(1)

    Object.defineProperty(window, 'location', { configurable: true, value: originalLocation })
  })
})
