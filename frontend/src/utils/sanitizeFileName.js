export function sanitizeFileName(name) {
  const parts = name.replace(/\\/g, '/').split('/')
  const last = parts[parts.length - 1].replace(/\.\./g, '')
  return last.trim() || '[arquivo]'
}
