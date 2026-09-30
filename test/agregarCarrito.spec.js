import { test, expect } from '@playwright/test'

test('agrega un producto al carrito', async ({ page }) => {
  await page.goto('/')

  await page.getByRole('button', { name: 'Agregar' }).first().click()

  await expect(page.getByRole('button', { name: 'Carrito (1)' })).toBeVisible()
})
