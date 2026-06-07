import '@testing-library/jest-dom'

// jsdom não expõe localStorage por padrão neste ambiente de teste.
// Polyfill simples baseado em Map para componentes que dependem dele (ex.: ThemeContext).
function makeStorageMock() {
  const store = new Map()
  return {
    getItem: (key) => (store.has(key) ? store.get(key) : null),
    setItem: (key, value) => store.set(key, String(value)),
    removeItem: (key) => store.delete(key),
    clear: () => store.clear(),
    key: (index) => Array.from(store.keys())[index] ?? null,
    get length() { return store.size },
  }
}

for (const target of [globalThis, typeof window !== 'undefined' ? window : undefined]) {
  if (!target) continue
  for (const prop of ['localStorage', 'sessionStorage']) {
    let needsMock = false
    try { needsMock = !target[prop] } catch { needsMock = true }
    if (needsMock) {
      try {
        Object.defineProperty(target, prop, { value: makeStorageMock(), configurable: true, writable: true })
      } catch { /* ambiente já fornece storage nativo */ }
    }
  }
}

if (typeof window !== 'undefined' && !window.matchMedia) {
  Object.defineProperty(window, 'matchMedia', {
    value: (query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
    configurable: true,
    writable: true,
  })
}
