import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: [] }),
    patch: vi.fn(),
  },
}))

import api from '../services/api'
import People from '../pages/People'
import Dashboard from '../pages/Dashboard'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('People page', () => {
  it('chama /people com limit=200, não 500', async () => {
    render(<MemoryRouter><People /></MemoryRouter>)
    await vi.waitFor(() => {
      expect(api.get).toHaveBeenCalled()
    })
    const calls = api.get.mock.calls.map((c) => c[0])
    const peopleCall = calls.find((url) => url.includes('/people'))
    expect(peopleCall).toBeDefined()
    expect(peopleCall).not.toContain('limit=500')
    expect(peopleCall).toContain('limit=200')
  })
})

describe('Dashboard page', () => {
  it('chama /people com limit=200, não 500', async () => {
    render(<MemoryRouter><Dashboard /></MemoryRouter>)
    await vi.waitFor(() => {
      expect(api.get).toHaveBeenCalled()
    })
    const calls = api.get.mock.calls.map((c) => c[0])
    const peopleCall = calls.find((url) => url.includes('/people'))
    expect(peopleCall).toBeDefined()
    expect(peopleCall).not.toContain('limit=500')
    expect(peopleCall).toContain('limit=200')
  })
})
