import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import MergeActionBar from './MergeActionBar'

describe('MergeActionBar', () => {
  it('does not render when no selections', () => {
    const { container } = render(
      <MergeActionBar selected={[]} primaryId={null} onSetPrimary={vi.fn()} onMerge={vi.fn()} onCancel={vi.fn()} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders selection count', () => {
    render(
      <MergeActionBar selected={[1, 2, 3]} primaryId={1} onSetPrimary={vi.fn()} onMerge={vi.fn()} onCancel={vi.fn()} />
    )
    expect(screen.getByText(/3 selecionad/i)).toBeInTheDocument()
  })

  it('disables merge button when no primary set', () => {
    render(
      <MergeActionBar selected={[1, 2]} primaryId={null} onSetPrimary={vi.fn()} onMerge={vi.fn()} onCancel={vi.fn()} />
    )
    expect(screen.getByRole('button', { name: /mesclar/i })).toBeDisabled()
  })

  it('enables merge button when primary is set and at least 2 selected', () => {
    render(
      <MergeActionBar selected={[1, 2]} primaryId={1} onSetPrimary={vi.fn()} onMerge={vi.fn()} onCancel={vi.fn()} />
    )
    expect(screen.getByRole('button', { name: /mesclar/i })).not.toBeDisabled()
  })

  it('calls onMerge when merge button clicked', () => {
    const onMerge = vi.fn()
    render(
      <MergeActionBar selected={[1, 2]} primaryId={1} onSetPrimary={vi.fn()} onMerge={onMerge} onCancel={vi.fn()} />
    )
    fireEvent.click(screen.getByRole('button', { name: /mesclar/i }))
    expect(onMerge).toHaveBeenCalledOnce()
  })

  it('calls onCancel when cancel button clicked', () => {
    const onCancel = vi.fn()
    render(
      <MergeActionBar selected={[1, 2]} primaryId={1} onSetPrimary={vi.fn()} onMerge={vi.fn()} onCancel={onCancel} />
    )
    fireEvent.click(screen.getByRole('button', { name: /cancelar/i }))
    expect(onCancel).toHaveBeenCalledOnce()
  })
})
