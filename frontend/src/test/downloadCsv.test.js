import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('downloadCsv', () => {
  let appendSpy, removeSpy, clickSpy, createObjectUrlSpy, revokeObjectUrlSpy
  let mockAnchor

  beforeEach(() => {
    clickSpy = vi.fn()
    mockAnchor = { href: '', download: '', click: clickSpy }

    appendSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => {})
    removeSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => {})
    vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor)

    createObjectUrlSpy = vi.fn().mockReturnValue('blob:fake-url')
    revokeObjectUrlSpy = vi.fn()
    global.URL.createObjectURL = createObjectUrlSpy
    global.URL.revokeObjectURL = revokeObjectUrlSpy
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('cria elemento <a> com href e download corretos', async () => {
    const { downloadCsv } = await import('../utils/downloadCsv.js')
    const blob = new Blob(['col1,col2'], { type: 'text/csv' })
    downloadCsv(blob, 'relatorio.csv')

    expect(createObjectUrlSpy).toHaveBeenCalledWith(blob)
    expect(mockAnchor.href).toBe('blob:fake-url')
    expect(mockAnchor.download).toBe('relatorio.csv')
  })

  it('chama click() no elemento', async () => {
    const { downloadCsv } = await import('../utils/downloadCsv.js')
    const blob = new Blob(['data'], { type: 'text/csv' })
    downloadCsv(blob, 'test.csv')
    expect(clickSpy).toHaveBeenCalledOnce()
  })

  it('revoga o object URL após o download', async () => {
    const { downloadCsv } = await import('../utils/downloadCsv.js')
    const blob = new Blob(['data'], { type: 'text/csv' })
    downloadCsv(blob, 'test.csv')
    expect(revokeObjectUrlSpy).toHaveBeenCalledWith('blob:fake-url')
  })
})
