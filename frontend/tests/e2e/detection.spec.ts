import { test, expect } from '@playwright/test'

test.describe('Detection', () => {
  test.beforeEach(async ({ page }) => {
    // Login first (assuming test user exists)
    await page.goto('/auth/login')
    await page.fill('input[type="text"]', 'test@example.com')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    // Wait for redirect
    await page.waitForURL('/', { timeout: 10000 })
  })

  test('should show home page after login', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Welcome to RumorLens')
  })

  test('should navigate to single detection', async ({ page }) => {
    await page.click('text=Single Detection')
    await expect(page).toHaveURL(/.*\/detection/)
    await expect(page.locator('h1')).toContainText('Rumor Detection')
  })

  test('should show detection form', async ({ page }) => {
    await page.goto('/detection')

    await expect(page.locator('textarea')).toBeVisible()
    await expect(page.locator('button:has-text("Analyze")')).toBeVisible()
  })

  test('should navigate to batch detection', async ({ page }) => {
    await page.click('text=Batch Detection')
    await expect(page).toHaveURL(/.*\/detection\/batch/)
    await expect(page.locator('h1')).toContainText('Batch Detection')
  })

  test('should navigate to history', async ({ page }) => {
    await page.click('text=History')
    await expect(page).toHaveURL(/.*\/history/)
    await expect(page.locator('h1')).toContainText('Detection History')
  })

  test('should navigate to dashboard', async ({ page }) => {
    await page.click('text=Dashboard')
    await expect(page).toHaveURL(/.*\/dashboard/)
    await expect(page.locator('h1')).toContainText('Analytics Dashboard')
  })
})
