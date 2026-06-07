import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

import PhotoModal from '../components/PhotoModal.jsx'

describe('PhotoModal', () => {
  const onClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    document.body.style.overflow = ''
  })

  it('não renderiza nada quando isOpen é false', () => {
    render(<PhotoModal isOpen={false} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('renderiza overlay e imagem com role="dialog" e aria-modal quando isOpen é true', () => {
    render(<PhotoModal isOpen={true} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    const dialog = screen.getByRole('dialog')
    expect(dialog).toBeTruthy()
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(screen.getByAltText('Foto de João')).toBeTruthy()
  })

  it('chama onClose ao pressionar Escape', () => {
    render(<PhotoModal isOpen={true} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalled()
  })

  it('chama onClose ao clicar no overlay (fora da imagem)', () => {
    render(<PhotoModal isOpen={true} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    fireEvent.click(screen.getByRole('dialog'))
    expect(onClose).toHaveBeenCalled()
  })

  it('NÃO chama onClose ao clicar na própria imagem (stopPropagation)', () => {
    render(<PhotoModal isOpen={true} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    fireEvent.click(screen.getByAltText('Foto de João'))
    expect(onClose).not.toHaveBeenCalled()
  })

  it('trava o scroll do body enquanto aberto e restaura ao fechar', () => {
    const { rerender } = render(<PhotoModal isOpen={true} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    expect(document.body.style.overflow).toBe('hidden')

    rerender(<PhotoModal isOpen={false} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    expect(document.body.style.overflow).toBe('')
  })

  it('botão de fechar possui aria-label acessível', () => {
    render(<PhotoModal isOpen={true} onClose={onClose} src="foto.jpg" alt="Foto de João" />)
    const closeBtn = screen.getByRole('button', { name: /fechar/i })
    fireEvent.click(closeBtn)
    expect(onClose).toHaveBeenCalled()
  })
})
