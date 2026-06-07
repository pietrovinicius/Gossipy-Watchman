import { describe, it, expect } from 'vitest'
import { parseUtcDate, formatDateTime } from './formatDate'

describe('parseUtcDate', () => {
  it('treats timestamp without timezone designator as UTC', () => {
    const d = parseUtcDate('2026-06-07T12:00:02.905879')
    expect(d.getUTCHours()).toBe(12)
    expect(d.getUTCMinutes()).toBe(0)
  })

  it('respects explicit Z designator', () => {
    const d = parseUtcDate('2026-06-07T12:00:02Z')
    expect(d.getUTCHours()).toBe(12)
  })

  it('respects explicit offset designator', () => {
    const d = parseUtcDate('2026-06-07T12:00:02-03:00')
    expect(d.getUTCHours()).toBe(15)
  })

  it('returns null for empty input', () => {
    expect(parseUtcDate(null)).toBeNull()
    expect(parseUtcDate('')).toBeNull()
  })
})

describe('formatDateTime', () => {
  it('formats a naive UTC timestamp converted to local time in pt-BR', () => {
    const result = formatDateTime('2026-06-07T12:00:02.905879')
    expect(result).toMatch(/^\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}$/)
  })

  it('returns empty string for falsy input', () => {
    expect(formatDateTime(null)).toBe('')
    expect(formatDateTime(undefined)).toBe('')
    expect(formatDateTime('')).toBe('')
  })
})
