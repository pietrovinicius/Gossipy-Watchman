import { test, expect } from '@playwright/test'

// Teste E2E: Clicar em "Definir como Principal" em PersonDetail
test('E2E: Set primary photo button should trigger API call', async ({ page, context }) => {
  // Configurar token JWT (assumindo admin/watchman)
  const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'  // Placeholder

  // Set token em sessionStorage
  await page.goto('http://localhost:5173/people/1', {
    waitUntil: 'networkidle',
  })

  await page.evaluate((t) => {
    sessionStorage.setItem('token', t)
  }, token)

  // Reload página com token
  await page.reload({ waitUntil: 'networkidle' })

  // Log network requests para debugar
  page.on('response', (response) => {
    console.log(`${response.request().method()} ${response.url()} ${response.status()}`)
  })

  // Aguarda "Frames detectados" section carregar
  await page.waitForSelector('text=Frames detectados', { timeout: 5000 })

  // Aguarda botão "Definir como principal" aparecer
  const setPrimaryButtons = await page.locator('button:has-text("Definir como principal")')
  const count = await setPrimaryButtons.count()

  console.log(`[E2E] Encontrados ${count} botões "Definir como principal"`)

  if (count === 0) {
    throw new Error('Nenhum botão "Definir como principal" encontrado na página')
  }

  // Monitorar chamadas PATCH
  const patchPromise = page.waitForResponse((response) =>
    response.url().includes('/people/') && response.url().includes('/primary-photo') && response.request().method() === 'PATCH'
  )

  // Clica primeiro botão
  await setPrimaryButtons.first().click()
  console.log('[E2E] Clicado em "Definir como principal"')

  // Aguarda resposta PATCH
  try {
    const patchResponse = await patchPromise
    console.log(`[E2E] PATCH respondeu com status ${patchResponse.status()}`)
    expect(patchResponse.status()).toBe(200)
  } catch (err) {
    console.log('[E2E] PATCH nunca foi chamado - BUG CONFIRMADO')
    throw err
  }

  // Verifica se mostrou "Definindo..."
  await page.waitForSelector('button:has-text("Definindo…")', { timeout: 2000 })
  console.log('[E2E] Botão mostrou "Definindo…"')
})

// Teste: Verificar se console.log está disparando
test('E2E: Console logs should show click handler fired', async ({ page }) => {
  const consoleLogs = []

  page.on('console', (msg) => {
    console.log(`[BROWSER CONSOLE] ${msg.text()}`)
    consoleLogs.push(msg.text())
  })

  await page.goto('http://localhost:5173/people/1', { waitUntil: 'networkidle' })

  await page.waitForSelector('text=Frames detectados', { timeout: 5000 })

  const setPrimaryButtons = await page.locator('button:has-text("Definir como principal")')
  await setPrimaryButtons.first().click()

  // Aguarda logs
  await page.waitForTimeout(1000)

  const handleSetPrimaryLog = consoleLogs.find((log) => log.includes('[PersonFrames] handleSetPrimary clicado'))

  if (!handleSetPrimaryLog) {
    console.log('❌ BUG: handleSetPrimary não foi disparado')
    console.log('Console logs:', consoleLogs)
    throw new Error('Click handler não disparou')
  }

  console.log('✅ Click handler disparou')
})
