import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should redirect to login when not authenticated', async ({ page }) => {
    await expect(page).toHaveURL(/.*\/auth\/login/)
  })

  test('should show login form', async ({ page }) => {
    await page.goto('/auth/login')

    await expect(page.locator('h2')).toContainText('Sign In')
    await expect(page.locator('input[type="text"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('should show register form', async ({ page }) => {
    await page.goto('/auth/register')

    await expect(page.locator('h2')).toContainText('Create Account')
    await expect(page.locator('input').first()).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('should navigate between login and register', async ({ page }) => {
    await page.goto('/auth/login')

    // Click on register link
    await page.click('text=Create one')
    await expect(page).toHaveURL(/.*\/auth\/register/)

    // Click on login link
    await page.click('text=Sign in')
    await expect(page).toHaveURL(/.*\/auth\/login/)
  })

  test('should show error for invalid login', async ({ page }) => {
    await page.goto('/auth/login')

    await page.fill('input[type="text"]', 'invalid@email.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    // Should show error message
    await expect(page.locator('.ant-message-error')).toBeVisible({ timeout: 10000 })
  })
})
