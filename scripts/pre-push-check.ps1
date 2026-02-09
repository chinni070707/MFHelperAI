#!/usr/bin/env pwsh
# Pre-Push Validation Script
# Runs basic code validation before pushing to Git

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Running pre-push validation checks..." -ForegroundColor Cyan

# Track if any checks fail
$failed = $false

# Change to project root (parent of scripts directory)
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot

# ============================================
# 1. Python Syntax Check (Compile)
# ============================================
Write-Host ""
Write-Host "Checking Python syntax..." -ForegroundColor Yellow

$pythonFiles = Get-ChildItem -Path "backend/app" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue

if ($pythonFiles) {
    $syntaxErrors = 0
    
    foreach ($file in $pythonFiles) {
        # Skip __pycache__ and .pyc files
        if ($file.FullName -match "__pycache__|\.pyc") {
            continue
        }
        
        # Compile Python file to check syntax
        $result = & python -m py_compile "$($file.FullName)" 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Syntax error in: $($file.Name)" -ForegroundColor Red
            Write-Host "  $result" -ForegroundColor Red
            $syntaxErrors++
            $failed = $true
        }
    }
    
    if ($syntaxErrors -eq 0) {
        Write-Host "  All Python files have valid syntax ($($pythonFiles.Count) files checked)" -ForegroundColor Green
    } else {
        Write-Host "  Found $syntaxErrors syntax error(s)" -ForegroundColor Red
    }
} else {
    Write-Host "  No Python files found to check" -ForegroundColor Yellow
}

# ============================================
# 2. Ruff Linting (catches undefined names, missing imports, etc.)
# ============================================
Write-Host ""
Write-Host "Running ruff lint checks..." -ForegroundColor Yellow

$ruffPath = Join-Path $projectRoot "venv\Scripts\ruff.exe"
if (-not (Test-Path $ruffPath)) {
    # Fallback: try system ruff
    $ruffPath = "ruff"
}

try {
    $ruffOutput = & $ruffPath check backend/app --select F821,F401,F811,F841 --no-fix 2>&1
    $ruffExitCode = $LASTEXITCODE

    if ($ruffExitCode -eq 0) {
        Write-Host "  Ruff lint passed (no undefined names, unused imports, or syntax errors)" -ForegroundColor Green
    } else {
        Write-Host "  Ruff found issues:" -ForegroundColor Red
        $ruffOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
        $failed = $true
    }
} catch {
    Write-Host "  Ruff not installed - skipping lint check" -ForegroundColor Yellow
    Write-Host "  Install with: pip install ruff" -ForegroundColor Yellow
}

# ============================================
# 2b. Import Validation
# ============================================
Write-Host ""
Write-Host "Validating Python imports..." -ForegroundColor Yellow

# Find python in venv or .venv
$pythonPath = $null
if (Test-Path (Join-Path $projectRoot "venv\Scripts\python.exe")) {
    $pythonPath = Join-Path $projectRoot "venv\Scripts\python.exe"
} elseif (Test-Path (Join-Path $projectRoot ".venv\Scripts\python.exe")) {
    $pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
} else {
    $pythonPath = "python"
}

Push-Location backend
try {
    $ErrorActionPreference = "SilentlyContinue"
    $importResult = & $pythonPath -c "import sys; import app.config; import app.main; sys.exit(0)" 2>&1 | Out-Null
    $importExitCode = $LASTEXITCODE
    $ErrorActionPreference = "Stop"

    if ($importExitCode -eq 0) {
        Write-Host "  Core imports validated successfully" -ForegroundColor Green
    } else {
        Write-Host "  Import validation failed - check config.py and main.py" -ForegroundColor Red
        $failed = $true
    }
} catch {
    Write-Host "  Import validation failed" -ForegroundColor Red
    $failed = $true
}
Pop-Location

# ============================================
# 3. Run Critical Tests (pytest)
# ============================================
Write-Host ""
Write-Host "Running critical tests (pytest)..." -ForegroundColor Yellow

Push-Location backend
try {
    # Check if pytest is installed
    $pytestPath = Join-Path $projectRoot "venv\Scripts\pytest.exe"
    if (-not (Test-Path $pytestPath)) {
        # Try .venv
        $pytestPath = Join-Path $projectRoot ".venv\Scripts\pytest.exe"
        if (-not (Test-Path $pytestPath)) {
            # Try system pytest
            $pytestPath = "pytest"
        }
    }

    # Run auth tests (critical for Google Sign-In)
    Write-Host "  Testing authentication..." -ForegroundColor Gray
    $authTestResult = & $pytestPath tests/test_auth.py -q --tb=no 2>&1
    $authExitCode = $LASTEXITCODE

    if ($authExitCode -eq 0) {
        Write-Host "  Auth tests passed ✓" -ForegroundColor Green
    } else {
        Write-Host "  Auth tests failed!" -ForegroundColor Red
        $authTestResult | Select-Object -Last 10 | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
        $failed = $true
    }

    # Run portfolio tests (critical for data handling)
    Write-Host "  Testing portfolio operations..." -ForegroundColor Gray
    $portfolioTestResult = & $pytestPath tests/test_portfolio.py -q --tb=no 2>&1
    $portfolioExitCode = $LASTEXITCODE

    if ($portfolioExitCode -eq 0) {
        Write-Host "  Portfolio tests passed ✓" -ForegroundColor Green
    } else {
        Write-Host "  Portfolio tests failed!" -ForegroundColor Red
        $portfolioTestResult | Select-Object -Last 10 | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
        $failed = $true
    }

    # Run upload tests (critical for CAS parsing)
    Write-Host "  Testing upload functionality..." -ForegroundColor Gray
    $uploadTestResult = & $pytestPath tests/test_upload.py -q --tb=no 2>&1
    $uploadExitCode = $LASTEXITCODE

    if ($uploadExitCode -eq 0) {
        Write-Host "  Upload tests passed ✓" -ForegroundColor Green
    } else {
        Write-Host "  Upload tests failed!" -ForegroundColor Red
        $uploadTestResult | Select-Object -Last 10 | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
        $failed = $true
    }

} catch {
    Write-Host "  Pytest not installed or not found - skipping tests" -ForegroundColor Yellow
    Write-Host "  Install with: pip install pytest" -ForegroundColor Yellow
}
Pop-Location

# ============================================
# 4. Check requirements.txt
# ============================================
Write-Host ""
Write-Host "Checking requirements.txt..." -ForegroundColor Yellow

if (Test-Path "backend/requirements.txt") {
    $reqContent = Get-Content "backend/requirements.txt" -Raw
    
    # Check for critical packages
    $criticalPackages = @("fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary")
    $missingPackages = @()
    
    foreach ($pkg in $criticalPackages) {
        if ($reqContent -notmatch $pkg) {
            $missingPackages += $pkg
        }
    }
    
    if ($missingPackages.Count -eq 0) {
        Write-Host "  All critical packages present in requirements.txt" -ForegroundColor Green
    } else {
        Write-Host "  Missing critical packages: $($missingPackages -join ', ')" -ForegroundColor Red
        $failed = $true
    }
} else {
    Write-Host "  requirements.txt not found!" -ForegroundColor Red
    $failed = $true
}

# ============================================
# 5. Check deployment files
# ============================================
Write-Host ""
Write-Host "Checking deployment files..." -ForegroundColor Yellow

$deploymentFiles = @("render.yaml", ".renderignore")
$missingFiles = @()

foreach ($file in $deploymentFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Host "  All deployment files present" -ForegroundColor Green
} else {
    Write-Host "  Missing deployment files: $($missingFiles -join ', ')" -ForegroundColor Yellow
}

# ============================================
# Summary
# ============================================
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan

if ($failed) {
    Write-Host "PRE-PUSH VALIDATION FAILED!" -ForegroundColor Red
    Write-Host "Fix the errors above before pushing." -ForegroundColor Yellow
    Write-Host "==================================================" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "Safe to push to Git." -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Cyan
    exit 0
}
