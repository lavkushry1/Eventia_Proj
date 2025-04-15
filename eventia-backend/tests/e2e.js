// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Eventia Ticketing Platform E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page before each test
    await page.goto('http://localhost:3000/');
  });

  test('Home page loads and shows events', async ({ page }) => {
    // Check if the page title is correct
    await expect(page).toHaveTitle(/Eventia/);
    
    // Check if events are displayed
    await expect(page.locator('.event-card')).toBeVisible();
    
    // Log network requests for debugging
    page.on('request', request => console.log(`>> Request: ${request.method()} ${request.url()}`));
    page.on('response', response => console.log(`<< Response: ${response.status()} ${response.url()}`));
    
    // Take a screenshot for verification
    await page.screenshot({ path: 'tests/screenshots/home-page.png' });
  });

  test('Event details page works', async ({ page }) => {
    // Wait for events to load and click on the first event
    await page.locator('.event-card').first().click();
    
    // Check if we're on the event details page
    await expect(page.locator('h1.event-title')).toBeVisible();
    await expect(page.locator('.event-details')).toBeVisible();
    
    // Check if booking section is displayed
    await expect(page.locator('.booking-section')).toBeVisible();
    
    // Take a screenshot for verification
    await page.screenshot({ path: 'tests/screenshots/event-details.png' });
  });

  test('Booking flow works end-to-end', async ({ page }) => {
    // Navigate to the first event details
    await page.locator('.event-card').first().click();
    
    // Select 2 tickets
    await page.locator('.quantity-selector button').nth(1).click();
    
    // Enter customer information
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="phone"]', '9876543210');
    
    // Submit booking
    await page.locator('button.booking-submit').click();
    
    // Wait for the payment page to appear
    await expect(page.locator('.payment-section')).toBeVisible();
    
    // Check if QR code is displayed
    await expect(page.locator('.payment-qr-code')).toBeVisible();
    
    // Enter UTR
    await page.fill('input[name="utr"]', 'UTR123456789');
    
    // Submit UTR
    await page.locator('button.utr-submit').click();
    
    // Check if ticket is generated
    await expect(page.locator('.ticket-confirmed')).toBeVisible();
    await expect(page.locator('.ticket-id')).toBeVisible();
    
    // Take a screenshot for verification
    await page.screenshot({ path: 'tests/screenshots/booking-complete.png' });
  });

  test('Error page is displayed for invalid routes', async ({ page }) => {
    // Navigate to an invalid route
    await page.goto('http://localhost:3000/invalid-route');
    
    // Check if 404 page is displayed
    await expect(page.locator('.error-page')).toBeVisible();
    await expect(page.locator('h1')).toContainText('404');
    
    // Take a screenshot for verification
    await page.screenshot({ path: 'tests/screenshots/404-page.png' });
  });
});

// Run the tests:
// npx playwright test tests/e2e.js --headed 