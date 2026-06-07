import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

import ConfirmModal from '../components/ConfirmModal.jsx'

describe('ConfirmModal', () => {
  const onConfirm = vi.fn()
  const onCancel = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('não renderiza nada quando isOpen é false', () => {
    render(
      <ConfirmModal
        isOpen={false}
        title="Excluir vídeo"
        message="Tem certeza?"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('renderiza título, mensagem e botões com role="dialog" e aria-modal quando isOpen é true', () => {
    render(
      <ConfirmModal
        isOpen={true}
        title="Excluir vídeo"
        message="Tem certeza?"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
    expect(screen.getByText('Excluir vídeo')).toBeTruthy()
    expect(screen.getByText('Tem certeza?')).toBeTruthy()
    expect(screen.getByRole('button', { name: /confirmar/i })).toBeTruthy()
    expect(screen.getByRole('button', { name: /cancelar/i })).toBeTruthy()
  })

  it('chama onConfirm ao clicar no botão de confirmação', () => {
    render(
      <ConfirmModal
        isOpen={true}
        title="Excluir vídeo"
        message="Tem certeza?"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    fireEvent.click(screen.getByRole('button', { name: /confirmar/i }))
    expect(onConfirm).toHaveBeenCalled()
  })

  it('chama onCancel ao clicar no botão de cancelamento', () => {
    render(
      <ConfirmModal
        isOpen={true}
        title="Excluir vídeo"
        message="Tem certeza?"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    fireEvent.click(screen.getByRole('button', { name: /cancelar/i }))
    expect(onCancel).toHaveBeenCalled()
  })

  it('chama onCancel ao pressionar Escape', () => {
    render(
      <ConfirmModal
        isOpen={true}
        title="Excluir vídeo"
        message="Tem certeza?"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onCancel).toHaveBeenCalled()
  })

  it('aplica classe de cor correspondente à variant "danger" no botão de confirmação', () => {
    render(
      <ConfirmModal
        isOpen={true}
        title="Excluir"
        message="Tem certeza?"
        variant="danger"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    const confirmBtn = screen.getByRole('button', { name: /confirmar/i })
    expect(confirmBtn.className).toMatch(/bg-red-600/)
  })

  it('com requireTyping, botão de confirmação inicia desabilitado e habilita só com a palavra correta digitada', () => {
    render(
      <ConfirmModal
        isOpen={true}
        title="Excluir perfil"
        message="Esta ação é irreversível."
        requireTyping={true}
        confirmWord="excluir"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    const confirmBtn = screen.getByRole('button', { name: /confirmar/i })
    const input = screen.getByRole('textbox')

    expect(confirmBtn).toBeDisabled()

    fireEvent.change(input, { target: { value: 'errado' } })
    expect(confirmBtn).toBeDisabled()

    fireEvent.change(input, { target: { value: 'excluir' } })
    expect(confirmBtn).not.toBeDisabled()

    fireEvent.click(confirmBtn)
    expect(onConfirm).toHaveBeenCalled()
  })

  it('usa confirmLabel e cancelLabel customizados quando fornecidos', () => {
    render(
      <ConfirmModal
        isOpen={true}
        title="Restaurar"
        message="Deseja restaurar?"
        confirmLabel="Restaurar"
        cancelLabel="Voltar"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )
    expect(screen.getByRole('button', { name: 'Restaurar' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Voltar' })).toBeTruthy()
  })
})
