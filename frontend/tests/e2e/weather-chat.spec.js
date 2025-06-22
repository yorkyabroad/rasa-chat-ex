const { test, expect } = require('@playwright/test');

test.describe('Weather Chat E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays the weather assistant interface', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Weather Assistant' })).toBeVisible();
    await expect(page.locator('text=Hello! I am your weather assistant')).toBeVisible();
    await expect(page.locator('textarea[placeholder="Ask about the weather..."]')).toBeVisible();
  });

  test('allows user to type and send a message', async ({ page }) => {
    const message = 'What is the weather in London?';
    
    const input = page.locator('textarea[placeholder="Ask about the weather..."]');
    await input.fill(message);
    await expect(input).toHaveValue(message);
    
    // Click the send button (last button in the page)
    const buttons = page.locator('button');
    await buttons.last().click();
    
    await expect(page.locator(`text=${message}`)).toBeVisible();
  });

  test('displays quick action buttons', async ({ page }) => {
    await expect(page.locator('text=Quick Actions')).toBeVisible();
    await expect(page.getByRole('button', { name: 'London' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'New York' })).toBeVisible();
    await expect(page.getByRole('button', { name: /Current weather/ })).toBeVisible();
    await expect(page.getByRole('button', { name: /Tomorrow forecast/ })).toBeVisible();
  });

  test('allows selection of location and weather request', async ({ page }) => {
    await page.getByRole('button', { name: 'London' }).click();
    await page.getByRole('button', { name: /Current weather/ }).click();
    
    await expect(page.locator('text=Ask: Current weather in London')).toBeVisible();
  });

  test('handles quick action submission', async ({ page }) => {
    // Mock the API response
    await page.route('**/webhooks/rest/webhook', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{ text: 'Mocked weather response' }])
      });
    });

    await page.getByRole('button', { name: 'London' }).click();
    await page.getByRole('button', { name: /Current weather/ }).click();
    await page.getByRole('button', { name: 'Ask: Current weather in London' }).click();
    
    await expect(page.locator('text=Current weather in London')).toBeVisible();
  });

  test('handles API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/webhooks/rest/webhook', async route => {
      await route.fulfill({ status: 500 });
    });
    
    const input = page.locator('textarea[placeholder="Ask about the weather..."]');
    await input.fill('Test message');
    
    const buttons = page.locator('button');
    await buttons.last().click();
    
    await expect(page.locator('text=Could not connect to the chatbot')).toBeVisible();
  });

  test('displays weather information panel on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await expect(page.locator('text=Weather Chatbot')).toBeVisible();
    await expect(page.locator('text=Features')).toBeVisible();
  });

  test('is responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.getByRole('heading', { name: 'Weather Assistant' })).toBeVisible();
    await expect(page.locator('textarea[placeholder="Ask about the weather..."]')).toBeVisible();
  });

  test('allows keyboard navigation', async ({ page }) => {
    const input = page.locator('textarea[placeholder="Ask about the weather..."]');
    await input.fill('Test message');
    await input.press('Enter');
    
    await expect(page.locator('text=Test message')).toBeVisible();
  });
});