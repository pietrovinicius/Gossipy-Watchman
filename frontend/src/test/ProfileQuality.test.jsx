import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../services/api', () => ({
  default: { get: vi.fn() },
}))

import api from '../services/api'
import ProfileQuality from '../components/ProfileQuality.jsx'

const QUALITY_GOOD = {
  avg_confidence: 0.3,
  sample_count: 5,
  quality_score: 70.0,
  quality_level: 'excelente',
  color: 'green',
  recommendation: 'Perfil com amostras de alta confiança. Nenhuma ação necessária.',
}

describe('ProfileQuality', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exibe estado de carregamento inicialmente', () => {
    api.get.mockReturnValue(new Promise(() => {}))
    const { container } = render(<ProfileQuality personId={3} />)
    expect(container.querySelector('.animate-pulse')).toBeTruthy()
  })

  it('busca GET /people/{id}/quality', async () => {
    api.get.mockResolvedValue({ data: QUALITY_GOOD })
    render(<ProfileQuality personId={3} />)
    await waitFor(() => expect(api.get).toHaveBeenCalledWith('/people/3/quality'))
  })

  it('exibe o score formatado em porcentagem', async () => {
    api.get.mockResolvedValue({ data: QUALITY_GOOD })
    render(<ProfileQuality personId={3} />)
    expect(await screen.findByText('70%')).toBeTruthy()
  })

  it('exibe o rótulo do nível de qualidade', async () => {
    api.get.mockResolvedValue({ data: QUALITY_GOOD })
    render(<ProfileQuality personId={3} />)
    expect(await screen.findByText(/excelente/i)).toBeTruthy()
  })

  it('exibe sinal colorido correspondente à cor retornada', async () => {
    api.get.mockResolvedValue({ data: QUALITY_GOOD })
    const { container } = render(<ProfileQuality personId={3} />)
    await screen.findByText(/excelente/i)
    expect(container.querySelector('[data-quality-signal="green"]')).toBeTruthy()
  })

  it('exibe a recomendação truncada com tooltip (title) com texto completo', async () => {
    api.get.mockResolvedValue({ data: QUALITY_GOOD })
    render(<ProfileQuality personId={3} />)
    const recommendation = await screen.findByTitle(QUALITY_GOOD.recommendation)
    expect(recommendation).toBeTruthy()
  })

  it('exibe mensagem de erro quando a busca falha', async () => {
    api.get.mockRejectedValue(new Error('falhou'))
    render(<ProfileQuality personId={3} />)
    expect(await screen.findByText(/erro ao carregar/i)).toBeTruthy()
  })
})
