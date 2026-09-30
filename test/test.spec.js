import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:5173/');
  await page.getByRole('searchbox', { name: 'Buscar productos' }).click();
  await page.getByRole('searchbox', { name: 'Buscar productos' }).fill('Powder');
  await page.getByRole('searchbox', { name: 'Buscar productos' }).press('Enter');
  await page.getByRole('article').filter({ hasText: 'Powder Canister$14.99Rating:' }).getByRole('button').click();
});