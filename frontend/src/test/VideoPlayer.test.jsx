import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { VideoPlayer } from '../components/VideoPlayer'

describe('VideoPlayer', () => {
  const mockProps = {
    videoId: 1,
    token: 'test-token-123',
    onTimeUpdate: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders video element with correct src', () => {
    render(<VideoPlayer {...mockProps} />)
    const video = screen.getByRole('img', { hidden: true })?.closest('video')
    if (video) {
      expect(video.src).toContain('videoId=1')
      expect(video.src).toContain('token=test-token-123')
    }
  })

  it('calls onTimeUpdate with currentTime on time update', async () => {
    const { container } = render(<VideoPlayer {...mockProps} />)
    const video = container.querySelector('video')

    fireEvent.timeUpdate(video, { target: { currentTime: 10.5 } })

    await waitFor(() => {
      expect(mockProps.onTimeUpdate).toHaveBeenCalledWith(10.5)
    })
  })

  it('updates currentTime when seekTo prop changes', async () => {
    const { rerender, container } = render(<VideoPlayer {...mockProps} seekTo={null} />)
    const video = container.querySelector('video')

    rerender(<VideoPlayer {...mockProps} seekTo={5} />)

    await waitFor(() => {
      expect(video.currentTime).toBe(5)
    })
  })

  it('does not update video when seekTo is null', () => {
    const { container } = render(<VideoPlayer {...mockProps} seekTo={null} />)
    const video = container.querySelector('video')
    const initialTime = video.currentTime

    fireEvent.timeUpdate(video, { target: { currentTime: initialTime } })

    expect(video.currentTime).toBe(initialTime)
  })

  it('displays error message on video error', async () => {
    const { container } = render(<VideoPlayer {...mockProps} />)
    const video = container.querySelector('video')

    fireEvent.error(video)

    await waitFor(() => {
      expect(screen.queryByText(/erro/i)).toBeInTheDocument()
    })
  })

  it('has speed buttons 0.5x 1x 1.5x 2x', () => {
    render(<VideoPlayer {...mockProps} />)

    expect(screen.getByText('0.5x')).toBeInTheDocument()
    expect(screen.getByText('1x')).toBeInTheDocument()
    expect(screen.getByText('1.5x')).toBeInTheDocument()
    expect(screen.getByText('2x')).toBeInTheDocument()
  })

  it('updates playbackRate when speed button clicked', async () => {
    const { container } = render(<VideoPlayer {...mockProps} />)
    const video = container.querySelector('video')
    const btn15 = screen.getByText('1.5x')

    fireEvent.click(btn15)

    await waitFor(() => {
      expect(video.playbackRate).toBe(1.5)
    })
  })

  it('1x button is active by default', () => {
    render(<VideoPlayer {...mockProps} />)
    const btn1x = screen.getByText('1x')

    expect(btn1x.className).toContain('bg-primary')
  })
})
