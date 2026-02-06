# 🧪 Automated Testing Guide

## Why We Need Automated Tests

**The Problem We Faced:**
- JavaScript syntax error (duplicate `}`) broke ALL buttons
- AMC dropdowns were empty due to race condition
- Manual testing took too long to catch these issues
- Issues only discovered after deployment

**The Solution:**
Comprehensive automated test suite that runs in **2-3 minutes** and catches:
- ✅ JavaScript syntax errors
- ✅ Button click functionality
- ✅ Modal opening/closing
- ✅ API integration issues
- ✅ Race conditions in async code
- ✅ UI element rendering
- ✅ Form validation

---

## 🚀 Quick Start

### Run All Tests (Windows):
```powershell
.\run-tests.ps1
```

### Run All Tests (Linux/Mac):
```bash
chmod +x run-tests.sh
./run-tests.sh
```

### Run Specific Test Suite:
```bash
cd tests
npx playwright test manual-entry.spec.ts    # Manual entry tests
npx playwright test file-upload.spec.ts     # File upload tests
npx playwright test dashboard-core.spec.ts  # Core dashboard tests
npx playwright test api-integration.spec.ts # API tests
```

---

## 📊 Test Coverage

### 1. **Manual Portfolio Entry Tests** (`manual-entry.spec.ts`)
- ✅ Modal opens with 5 rows
- ✅ AMC dropdowns are populated
- ✅ Fund search enables after AMC selection
- ✅ Auto-suggestions appear when typing
- ✅ Add row button works
- ✅ Buttons are equal width
- ✅ Validation prevents empty submissions
- ✅ Cancel closes modal
- ✅ No JavaScript errors

**Time:** ~10 seconds

### 2. **File Upload Tests** (`file-upload.spec.ts`)
- ✅ Upload modal opens
- ✅ PDF password field shows for PDFs
- ✅ Upload button enables after file selection
- ✅ Cancel closes modal
- ✅ No JavaScript errors

**Time:** ~5 seconds

### 3. **Dashboard Core Tests** (`dashboard-core.spec.ts`)
- ✅ Page loads without errors
- ✅ All main buttons visible
- ✅ All buttons clickable
- ✅ No duplicate closing braces
- ✅ No console errors/warnings

**Time:** ~8 seconds

### 4. **API Integration Tests** (`api-integration.spec.ts`)
- ✅ AMC list endpoint works
- ✅ Fund search by AMC works
- ✅ Keyword search works
- ✅ Health check passes
- ✅ CORS headers present
- ✅ No 500 errors on valid requests

**Time:** ~5 seconds

### 5. **JavaScript Validation** (`javascript-validation.spec.ts`)
- ✅ No syntax errors in all pages
- ✅ No duplicate closing braces
- ✅ Functions are defined
- ✅ Async/await properly used

**Time:** ~3 seconds

---

## 🔄 Continuous Integration

Tests run automatically on **every commit** to `main` branch via GitHub Actions:

1. **Triggered on:**
   - Push to `main`
   - Pull requests to `main`
   - Changes to `frontend/`, `backend/app/routes/`, or `tests/`

2. **What happens:**
   - Backend server starts
   - All E2E tests run
   - Test report uploaded
   - ❌ Commit blocked if tests fail

3. **View results:**
   - GitHub → Actions tab
   - See detailed test report
   - Download Playwright HTML report

---

## 🎯 What Each Test Catches

### JavaScript Syntax Errors
```javascript
// BAD - Would be caught:
function save() {
    // code
}
}  // ← Extra brace!

// GOOD:
function save() {
    // code
}
```

### Race Conditions
```javascript
// BAD - Would be caught:
function showModal() {
    addRows();  // Runs immediately
    loadData(); // Async, completes later
}

// GOOD:
async function showModal() {
    await loadData();  // Wait first
    addRows();         // Then render
}
```

### Missing API Data
```javascript
// Tests verify:
- API returns success: true
- Data arrays are not empty
- All required fields present
- No 500 errors
```

### UI Elements
```javascript
// Tests verify:
- Buttons are visible
- Buttons are clickable
- Modals open/close
- Forms validate input
- Dropdowns have options
```

---

## 📝 Adding New Tests

### Example: Test a new feature
```typescript
test('should do something', async ({ page }) => {
  // 1. Navigate
  await page.goto('http://localhost:8000/dashboard.html');
  
  // 2. Interact
  await page.click('text=My Button');
  
  // 3. Verify
  await expect(page.locator('#myElement')).toBeVisible();
  
  console.log('✅ Feature works!');
});
```

---

## 🐛 Debugging Failed Tests

### View detailed output:
```bash
cd tests
npx playwright test --debug           # Step through tests
npx playwright test --headed          # See browser
npx playwright show-report            # View HTML report
```

### Common issues:

**Backend not running:**
```bash
# Start manually:
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test timeout:**
```typescript
// Increase timeout for slow operations:
test.setTimeout(60000); // 60 seconds
```

**Element not found:**
```typescript
// Add wait:
await page.waitForSelector('#myElement');
await page.waitForLoadState('networkidle');
```

---

## ⚡ Performance

| Test Suite | Duration | Tests |
|------------|----------|-------|
| Manual Entry | ~10s | 9 tests |
| File Upload | ~5s | 5 tests |
| Dashboard Core | ~8s | 5 tests |
| API Integration | ~5s | 6 tests |
| JavaScript Validation | ~3s | 4 tests |
| **TOTAL** | **~31s** | **29 tests** |

---

## 🎓 Best Practices

1. **Run tests before committing:**
   ```bash
   ./run-tests.ps1
   git commit -m "feat: New feature"
   ```

2. **Write tests for new features:**
   - Add test file in `tests/e2e/`
   - Follow existing patterns
   - Include console error checks

3. **Keep tests fast:**
   - Use `waitForTimeout` sparingly
   - Prefer `waitForSelector` or `waitForLoadState`
   - Test critical paths only

4. **Make tests reliable:**
   - Check for loading states
   - Handle async operations
   - Avoid hardcoded sleeps

---

## 📚 Resources

- **Playwright Docs:** https://playwright.dev/
- **Test Examples:** See `tests/e2e/*.spec.ts`
- **GitHub Actions:** `.github/workflows/frontend-validation.yml`
- **CI/CD Dashboard:** GitHub → Actions tab

---

## 🎉 Benefits

**Before Automated Tests:**
- ❌ Found bugs after deployment
- ❌ 15+ minutes of manual testing per change
- ❌ Missed edge cases
- ❌ Regression issues

**After Automated Tests:**
- ✅ Catch bugs in 30 seconds
- ✅ Test every commit automatically
- ✅ Cover edge cases systematically
- ✅ Prevent regressions
- ✅ Confidence in deployments

---

## 🚦 Test Status

Current test coverage:
- ✅ Manual portfolio entry
- ✅ File upload
- ✅ Dashboard core functionality
- ✅ API integration
- ✅ JavaScript validation

To add:
- ⏳ Authentication flow
- ⏳ Data export
- ⏳ Visual regression tests
- ⏳ Mobile responsive tests

---

**Questions?** Check the test output or review existing test files in `tests/e2e/`.
