import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { VideoPlayer } from '../components/VideoPlayer'

describe('VideoPlayer — Barra de Presença', () => {
  const mockOnSeek = vi.fn()
  const mockOnTimeUpdate = vi.fn()
  const mockOnDurationChange = vi.fn()
  const mockOnPlay = vi.fn()
  const mockOnPause = vi.fn()

  const mockPeople = [
    {
      person_id: 1,
      person_name: 'Alice',
      person_category: 'Funcionário',
      appearances: [
        { id: 101, timestamp_start: 5, timestamp_end: 15, confidence: 0.85 },
        { id: 102, timestamp_start: 30, timestamp_end: 40, confidence: 0.9 },
      ],
    },
    {
      person_id: 2,
      person_name: 'Bob',
      person_category: 'Visitante',
      appearances: [
        { id: 201, timestamp_start: 10, timestamp_end: 25, confidence: 0.8 },
      ],
    },
  ]

  const baseProps = {
    videoId: 'test-video-1',
    token: 'test-token',
    people: mockPeople,
    duration: 60,
    currentTime: 0,
    onSeek: mockOnSeek,
    onTimeUpdate: mockOnTimeUpdate,
    onDurationChange: mockOnDurationChange,
    onPlay: mockOnPlay,
    onPause: mockOnPause,
    seekTo: null,
  }

  it('barra de presença renderiza quando people e duration fornecidos', () => {
    const { container } = render(<VideoPlayer {...baseProps} />)

    const bar = container.querySelector('[data-testid="presence-bar"]')
    expect(bar).toBeTruthy()
  })

  it('segmento posicionado em left% correto baseado em timestamp_start', () => {
    const { container } = render(<VideoPlayer {...baseProps} />)

    // Primeiro segmento de Alice: 5s de 60s = 8.33%
    const segment = container.querySelector('[data-testid="presence-segment-101"]')
    const style = window.getComputedStyle(segment)
    const leftValue = parseFloat(style.left)
    expect(leftValue).toBeCloseTo(8.33, 1)
  })

  it('segmento com width mínimo de 0.5% quando aparição muito curta', () => {
    const shortAppearancePeople = [
      {
        person_id: 3,
        person_name: 'Charlie',
        person_category: 'Monitorado',
        appearances: [
          { id: 301, timestamp_start: 20, timestamp_end: 20.1, confidence: 0.7 },
        ],
      },
    ]

    const { container } = render(
      <VideoPlayer {...baseProps} people={shortAppearancePeople} />
    )

    const segment = container.querySelector('[data-testid="presence-segment-301"]')
    const style = window.getComputedStyle(segment)
    const widthValue = parseFloat(style.width)
    expect(widthValue).toBeGreaterThanOrEqual(0.5)
  })

  it('playhead posicionado em left% correto baseado em currentTime', () => {
    const { container, rerender } = render(
      <VideoPlayer {...baseProps} currentTime={15} />
    )

    const playhead = container.querySelector('[data-testid="presence-playhead"]')
    const style = window.getComputedStyle(playhead)
    const leftValue = parseFloat(style.left)
    // 15s de 60s = 25%
    expect(leftValue).toBeCloseTo(25, 1)

    // Atualizar currentTime para 45s
    rerender(
      <VideoPlayer {...baseProps} currentTime={45} />
    )
    const updatedPlayhead = container.querySelector(
      '[data-testid="presence-playhead"]'
    )
    const updatedStyle = window.getComputedStyle(updatedPlayhead)
    const updatedLeft = parseFloat(updatedStyle.left)
    // 45s de 60s = 75%
    expect(updatedLeft).toBeCloseTo(75, 1)
  })

  it('clicar em segmento chama onSeek com timestamp_start correto', () => {
    const { container } = render(<VideoPlayer {...baseProps} />)

    const segment = container.querySelector('[data-testid="presence-segment-101"]')
    fireEvent.click(segment)

    expect(mockOnSeek).toHaveBeenCalledWith(5)
  })

  it('legenda exibe nome de cada pessoa', () => {
    render(<VideoPlayer {...baseProps} />)

    expect(screen.getByText('Alice')).toBeTruthy()
    expect(screen.getByText('Bob')).toBeTruthy()
  })

  it('exibe botões de velocidade incluindo 6x, 10x, 25x, 50x e 100x', () => {
    render(<VideoPlayer {...baseProps} />)
    expect(screen.getByText('6x')).toBeTruthy()
    expect(screen.getByText('10x')).toBeTruthy()
    expect(screen.getByText('25x')).toBeTruthy()
    expect(screen.getByText('50x')).toBeTruthy()
    expect(screen.getByText('100x')).toBeTruthy()
  })

  it('barra não renderiza quando duration = 0', () => {
    const { container } = render(<VideoPlayer {...baseProps} duration={0} />)

    const bar = container.querySelector('[data-testid="presence-bar"]')
    expect(bar).toBeFalsy()
  })

  it('cores dos segmentos correspondem à categoria de pessoa', () => {
    const { container } = render(<VideoPlayer {...baseProps} />)

    // Alice: Funcionário = azul (#3B82F6) = rgb(59, 130, 246)
    const aliceSegment = container.querySelector('[data-testid="presence-segment-101"]')
    const aliceStyle = window.getComputedStyle(aliceSegment)
    expect(aliceStyle.backgroundColor).toBe('rgb(59, 130, 246)')

    // Bob: Visitante = roxo (#8B5CF6) = rgb(139, 92, 246)
    const bobSegment = container.querySelector('[data-testid="presence-segment-201"]')
    const bobStyle = window.getComputedStyle(bobSegment)
    expect(bobStyle.backgroundColor).toBe('rgb(139, 92, 246)')
  })
})
