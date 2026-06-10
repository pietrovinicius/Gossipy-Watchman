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
  it('formats a naive UTC timestamp converted to local time in pt-BR by default', () => {
    const result = formatDateTime('2026-06-07T12:00:02.905879')
    expect(result).toMatch(/^\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}$/)
  })

  it('formats a naive UTC timestamp in pt-BR locale as DD/MM/YYYY, HH:mm', () => {
    const result = formatDateTime('2026-06-07T12:00:02.905879', 'pt-BR')
    expect(result).toMatch(/^\d{2}\/\d{2}\/\d{4}, \d{2}:\d{2}$/)
  })

  it('formats a naive UTC timestamp in en locale as M/D/YYYY, h:mm AM/PM', () => {
    const result = formatDateTime('2026-06-07T12:00:02.905879', 'en')
    expect(result).toMatch(/^\d{1,2}\/\d{1,2}\/\d{4}, \d{1,2}:\d{2}\s?(AM|PM)$/)
  })

  it('returns empty string for falsy input', () => {
    expect(formatDateTime(null)).toBe('')
    expect(formatDateTime(undefined)).toBe('')
    expect(formatDateTime('')).toBe('')
  })
})
