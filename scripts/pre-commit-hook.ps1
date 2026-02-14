# Pre-commit hook (PowerShell) to run tests before committing
# This ensures no broken code reaches the repository

$ErrorActionPreference = "Continue"
$FAILED = $false

# Configuration - Set to $false to skip backend tests (for quick commits)
$RUN_BACKEND_TESTS = $false  # Change to $true to enable full test suite

Write-Host ""
Write-Host "Running pre-commit checks..." -ForegroundColor Cyan
Write-Host ""

# 1. Test Database Connection
Write-Host "Testing database connection..." -ForegroundColor Yellow
try {
    $result = python backend\test_db_connection.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[PASS] Database tests passed" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "[FAIL] Database tests failed" -ForegroundColor Red
        Write-Host ""
        $FAILED = $true
    }
} catch {
    Write-Host "[FAIL] Database tests failed: $_" -ForegroundColor Red
    Write-Host ""
    $FAILED = $true
}

# 2. Run Backend Tests (Optional - can be disabled for speed)
if ($RUN_BACKEND_TESTS) {
    Write-Host "Running backend tests..." -ForegroundColor Yellow
    Push-Location backend
    try {
        $result = python -m pytest tests/ -v --tb=short -x --maxfail=3
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[PASS] Backend tests passed" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host "[FAIL] Backend tests failed" -ForegroundColor Red
            Write-Host ""
            $FAILED = $true
        }
    } catch {
        Write-Host "[FAIL] Backend tests failed: $_" -ForegroundColor Red
        Write-Host ""
        $FAILED = $true
    }
    Pop-Location
} else {
    Write-Host "Skipping backend tests (disabled for speed)" -ForegroundColor Gray
    Write-Host "To enable: Edit scripts\pre-commit-hook.ps1 and set RUN_BACKEND_TESTS=`$true" -ForegroundColor Gray
    Write-Host ""
}

# 3. Check Python syntax for staged files
Write-Host "Checking Python syntax..." -ForegroundColor Yellow
$stagedFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.py$' }
if ($stagedFiles) {
    $syntaxErrors = $false
    foreach ($file in $stagedFiles) {
        $result = python -m py_compile $file 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] Syntax error in $file" -ForegroundColor Red
            $syntaxErrors = $true
            $FAILED = $true
        }
    }
    if (-not $syntaxErrors) {
        Write-Host "[PASS] Python syntax checks passed" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
    }
} else {
    Write-Host "No Python files to check" -ForegroundColor Gray
    Write-Host ""
}

# Final result
if ($FAILED) {
    Write-Host "PRE-COMMIT CHECKS FAILED" -ForegroundColor Red
    Write-Host "Please fix the issues before committing." -ForegroundColor Red
    Write-Host ""
    exit 1
} else {
    Write-Host "ALL PRE-COMMIT CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    exit 0
}
