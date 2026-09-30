import { test, expect } from '@playwright/test'

test('busca un producto aunque se escriba en minusculas', async ({ page }) => {
  await page.goto('/')

  await page.getByLabel('Buscar productos').fill('essence')

  await expect(page.getByRole('heading', { name: /Essence/i })).toBeVisible()
})

