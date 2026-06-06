import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import CategoryBadge from './CategoryBadge'

describe('CategoryBadge', () => {
  it('renders the category label', () => {
    render(<CategoryBadge category="Funcionário" />)
    expect(screen.getByText('Funcionário')).toBeInTheDocument()
  })

  it('renders Desconhecido as fallback when category is null', () => {
    render(<CategoryBadge category={null} />)
    expect(screen.getByText('Desconhecido')).toBeInTheDocument()
  })

  it('applies distinct color class for Funcionário', () => {
    const { container } = render(<CategoryBadge category="Funcionário" />)
    const badge = container.firstChild
    expect(badge.className).toMatch(/funcionario|blue|green/)
  })

  it('applies distinct color class for Monitorado', () => {
    const { container } = render(<CategoryBadge category="Monitorado" />)
    const badge = container.firstChild
    expect(badge.className).toMatch(/monitorado|red|orange/)
  })

  it('applies distinct color class for Visitante', () => {
    const { container } = render(<CategoryBadge category="Visitante" />)
    const badge = container.firstChild
    expect(badge.className).toMatch(/visitante|purple|yellow/)
  })
})
