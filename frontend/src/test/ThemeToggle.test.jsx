import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

vi.mock('../services/api', () => ({
  default: { get: vi.fn(() => Promise.resolve({ data: { unseen: 0 } })) },
  BACKEND_URL: 'http://localhost:8000',
}))

const toggleThemeMock = vi.fn()
let mockTheme = 'dark'

vi.mock('../contexts/ThemeContext', () => ({
  useTheme: () => ({ theme: mockTheme, toggleTheme: toggleThemeMock }),
}))

async function renderLayout() {
  const { default: Layout } = await import('../components/Layout.jsx')
  return render(
    <MemoryRouter>
      <Layout>conteúdo</Layout>
    </MemoryRouter>
  )
}

describe('ThemeToggle (dentro da Sidebar)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockTheme = 'dark'
  })

  it('exibe ícone Sun quando tema atual é "dark"', async () => {
    mockTheme = 'dark'
    const { container } = await renderLayout()

    expect(container.querySelector('.lucide-sun')).toBeTruthy()
  })

  it('exibe ícone Moon quando tema atual é "light"', async () => {
    mockTheme = 'light'
    const { container } = await renderLayout()

    expect(container.querySelector('.lucide-moon')).toBeTruthy()
  })

  it('clicar no botão chama toggleTheme', async () => {
    mockTheme = 'dark'
    await renderLayout()

    const [button] = screen.getAllByRole('button', { name: /light mode/i })
    fireEvent.click(button)

    expect(toggleThemeMock).toHaveBeenCalledTimes(1)
  })

  it('tem aria-label "Light mode" quando tema é dark e "Dark mode" quando tema é light', async () => {
    mockTheme = 'dark'
    const { unmount } = await renderLayout()
    expect(screen.getAllByRole('button', { name: 'Light mode' }).length).toBeGreaterThan(0)
    unmount()

    mockTheme = 'light'
    await renderLayout()
    expect(screen.getAllByRole('button', { name: 'Dark mode' }).length).toBeGreaterThan(0)
  })

  it('botão tem cursor-pointer', async () => {
    mockTheme = 'dark'
    await renderLayout()

    const [button] = screen.getAllByRole('button', { name: /light mode/i })
    expect(button.className).toContain('cursor-pointer')
  })
})
