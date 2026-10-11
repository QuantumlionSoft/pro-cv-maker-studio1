import { describe, expect, it } from 'vitest'
import { fieldError } from '@/utils/errors'
import { formatDateTime } from '@/utils/format'

describe('helpers', () => {
  it('returns the first field message or an empty string', () => {
    expect(fieldError({ title: ['Give it a name.', 'x'] }, 'title')).toBe('Give it a name.')
    expect(fieldError({}, 'title')).toBe('')
  })
  it('formats missing dates as a dash', () => {
    expect(formatDateTime(null)).toBe('—')
    expect(formatDateTime('not a date')).toBe('—')
  })
})
