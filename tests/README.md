# MFHelper Web Application Testing

Comprehensive Playwright test suite for the MFHelper mutual fund portfolio management application.

## 🎯 Test Coverage

### Test Suites

1. **Homepage Tests** (`e2e/homepage.spec.ts`)
   - Homepage loading and navigation
   - Responsive design verification
   - Console log monitoring
   - Link navigation

2. **AI Assistant Tests** (`e2e/ai-assistant.spec.ts`)
   - AI chat interface verification
   - Message sending and receiving
   - Error handling
   - Portfolio analysis features

3. **Form Interaction Tests** (`e2e/forms.spec.ts`)
   - Form input handling
   - Dropdown selections
   - Button interactions
   - Search functionality
   - Error handling (404 pages, network errors)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd tests
npm install
```

### 2. Install Playwright Browsers

```bash
npm run test:install
```

### 3. Run Tests

```bash
# Run all tests
npm test

# Run in headed mode (see the browser)
npm run test:headed

# Run with debug UI
npm run test:ui

# Run specific browser
npm run test:chrome
npm run test:firefox
npm run test:webkit

# Run mobile tests
npm run test:mobile
```

## 📊 Test Reports

### View HTML Report

```bash
npm run test:report
```

Reports are saved in:
- `test-results/html/` - HTML report
- `test-results/results.json` - JSON results
- `test-results/screenshots/` - Screenshots

## 🔧 Configuration

### Environment Variables

Create `.env` file in `tests/` directory:

```env
BASE_URL=http://localhost:5173
TIMEOUT=60000
```

### Playwright Config

Key settings in `playwright.config.ts`:
- **Base URL**: `http://localhost:5173`
- **Retries**: 2 in CI, 0 locally
- **Screenshots**: On failure
- **Videos**: On failure
- **Trace**: On first retry

## 🧪 Test Patterns (webapp-testing skill)

### Pattern: Wait for Element
```typescript
await page.waitForSelector('#element-id', { state: 'visible' });
```

### Pattern: Check if Element Exists
```typescript
const exists = await page.locator('#element-id').count() > 0;
```

### Pattern: Capture Screenshot
```typescript
await page.screenshot({ path: 'screenshot.png', fullPage: true });
```

### Pattern: Handle Errors
```typescript
try {
  await page.click('#button');
} catch (error) {
  await page.screenshot({ path: 'error.png' });
  throw error;
}
```

## 📁 Project Structure

```
tests/
├── e2e/                    # Test files
│   ├── homepage.spec.ts    # Homepage tests
│   ├── ai-assistant.spec.ts # AI feature tests
│   └── forms.spec.ts       # Form interaction tests
├── helpers/                # Helper utilities
│   └── test-helpers.ts     # Common test utilities
├── test-results/          # Test output
│   ├── html/             # HTML reports
│   ├── screenshots/       # Screenshots
│   └── results.json       # JSON results
├── playwright.config.ts   # Playwright configuration
├── package.json          # Dependencies & scripts
└── README.md             # This file
```

## 🎓 Helper Functions

Located in `helpers/test-helpers.ts`:

- `waitForCondition()` - Wait for custom condition
- `captureConsoleLogs()` - Capture browser console
- `captureScreenshot()` - Auto-named screenshots
- `waitForElement()` - Wait for element with retry
- `elementExists()` - Check element existence
- `fillForm()` - Fill form with data object
- `clickWithRetry()` - Click with retry logic
- `verifyNoConsoleErrors()` - Check for console errors

## 🌐 Browser Support

Tests run on:
- ✅ **Desktop**: Chrome, Firefox, Safari
- ✅ **Mobile**: Chrome (Pixel 5), Safari (iPhone 12)

## 📝 Writing New Tests

### 1. Create Test File

```bash
# Create new spec file
touch e2e/my-feature.spec.ts
```

### 2. Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('My Feature', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Test code here
    await expect(page).toHaveTitle(/MFHelper/);
  });
});
```

### 3. Use Helper Functions

```typescript
import { waitForElement, captureScreenshot } from '../helpers/test-helpers';

test('example', async ({ page }) => {
  await waitForElement(page, '#my-element');
  await captureScreenshot(page, 'my-feature');
});
```

## 🔍 Debugging Tests

### Debug Mode
```bash
npm run test:debug
```

### UI Mode (Recommended)
```bash
npm run test:ui
```

### View Trace
1. Run test with trace enabled (default on first retry)
2. Find trace file in `test-results/`
3. View with: `npx playwright show-trace trace.zip`

## ⚙️ CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install dependencies
  run: |
    cd tests
    npm install
    
- name: Install Playwright browsers
  run: |
    cd tests
    npm run test:install

- name: Run tests
  run: |
    cd tests
    npm test

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: tests/test-results/
```

## 📚 Guidelines (webapp-testing skill)

1. ✅ **Always verify app is running** - Check server before tests
2. ✅ **Use explicit waits** - Wait for elements/navigation
3. ✅ **Capture screenshots on failure** - Debug issues
4. ✅ **Clean up resources** - Close browser when done
5. ✅ **Handle timeouts gracefully** - Set reasonable timeouts
6. ✅ **Test incrementally** - Start simple before complex
7. ✅ **Use selectors wisely** - Prefer data-testid or roles

## 🚨 Troubleshooting

### Tests Fail to Start
```bash
# Reinstall browsers
npm run test:install

# Check if dev server is running
cd ../frontend && npm run dev
```

### Timeout Errors
- Increase timeout in `playwright.config.ts`
- Check network latency
- Verify application is accessible

### Element Not Found
- Add explicit waits
- Check selector accuracy
- Verify element is visible in DOM

## 📖 Resources

- [Playwright Documentation](https://playwright.dev)
- [webapp-testing Skill](.github/skills/webapp-testing/SKILL.md)
- [MFHelper Documentation](../README.md)

## 🤝 Contributing

1. Write tests following existing patterns
2. Use helper functions from `test-helpers.ts`
3. Add screenshots for visual verification
4. Update this README for new test suites
5. Follow webapp-testing skill guidelines
