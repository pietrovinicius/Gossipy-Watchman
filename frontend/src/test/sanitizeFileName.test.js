import { describe, it, expect } from 'vitest'
import { sanitizeFileName } from '../utils/sanitizeFileName'

describe('sanitizeFileName', () => {
  it('"../../etc/passwd.mp4" → "passwd.mp4"', () => {
    expect(sanitizeFileName('../../etc/passwd.mp4')).toBe('passwd.mp4')
  })

  it('"video_normal.mp4" → "video_normal.mp4"', () => {
    expect(sanitizeFileName('video_normal.mp4')).toBe('video_normal.mp4')
  })

  it('"subdir/video.mp4" → "video.mp4"', () => {
    expect(sanitizeFileName('subdir/video.mp4')).toBe('video.mp4')
  })

  it('string vazia → "[arquivo]"', () => {
    expect(sanitizeFileName('')).toBe('[arquivo]')
  })

  it('apenas ".." → "[arquivo]"', () => {
    expect(sanitizeFileName('..')).toBe('[arquivo]')
  })

  it('backslash Windows "dir\\\\file.mp4" → "file.mp4"', () => {
    expect(sanitizeFileName('dir\\file.mp4')).toBe('file.mp4')
  })
})
