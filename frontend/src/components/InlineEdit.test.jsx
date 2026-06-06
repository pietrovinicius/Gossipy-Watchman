import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import InlineEdit from './InlineEdit'

describe('InlineEdit', () => {
  it('renders value as text in view mode', () => {
    render(<InlineEdit value="João Silva" onSave={vi.fn()} />)
    expect(screen.getByText('João Silva')).toBeInTheDocument()
    expect(screen.queryByRole('textbox')).toBeNull()
  })

  it('switches to input on click', () => {
    render(<InlineEdit value="Maria" onSave={vi.fn()} />)
    fireEvent.click(screen.getByText('Maria'))
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Maria')).toBeInTheDocument()
  })

  it('calls onSave with new value on Enter', async () => {
    const onSave = vi.fn()
    render(<InlineEdit value="Antigo" onSave={onSave} />)
    fireEvent.click(screen.getByText('Antigo'))
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'Novo Nome' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    await waitFor(() => expect(onSave).toHaveBeenCalledWith('Novo Nome'))
  })

  it('cancels edit on Escape without calling onSave', () => {
    const onSave = vi.fn()
    render(<InlineEdit value="Original" onSave={onSave} />)
    fireEvent.click(screen.getByText('Original'))
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'Modificado' } })
    fireEvent.keyDown(input, { key: 'Escape' })
    expect(onSave).not.toHaveBeenCalled()
    expect(screen.getByText('Original')).toBeInTheDocument()
  })

  it('does not call onSave if value is empty or unchanged', async () => {
    const onSave = vi.fn()
    render(<InlineEdit value="Teste" onSave={onSave} />)
    fireEvent.click(screen.getByText('Teste'))
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: '' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(onSave).not.toHaveBeenCalled()
  })

  it('saves on blur when value changed', async () => {
    const onSave = vi.fn()
    render(<InlineEdit value="Original" onSave={onSave} />)
    fireEvent.click(screen.getByText('Original'))
    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'Novo' } })
    fireEvent.blur(input)
    await waitFor(() => expect(onSave).toHaveBeenCalledWith('Novo'))
  })
})
