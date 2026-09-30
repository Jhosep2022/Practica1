import { test, expect } from '@playwright/test'

test('busca un producto por nombre', async ({ page }) => {
  await page.goto('/')
await page.goto('chrome-error://chromewebdata/');
await page.goto('http://localhost:5173/');
  await page.getByLabel('Buscar productos').fill('Essence')

  await expect(page.getByRole('heading', { name: /Essence/i })).toBeVisible()
})
