#!/usr/bin/env pwsh
# Repository Cleanup Script
# Removes test files and adds them to .gitignore

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Repository Cleanup Script" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Files to remove
$filesToRemove = @(
    "backend/cas_extracted_text.txt",
    "backend/cas_parsed_data.json",
    "backend/cas_parsed_nsdl.json",
    "backend/kfintech_cas_parsed.json"
)

Write-Host "Step 1: Removing test/demo files from repository..." -ForegroundColor Yellow
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Write-Host "  Removing: $file" -ForegroundColor Gray
        git rm --cached $file 2>$null
    }
}

Write-Host ""
Write-Host "Step 2: Updating .gitignore..." -ForegroundColor Yellow

$gitignoreAdditions = @"

# Test/Demo CAS files (should not be in repo)
backend/cas_*.json
backend/cas_*.txt
backend/*_parsed*.json

# Reference files from other sites
acorns_*.css
acorns_*.html
"@

Add-Content -Path ".gitignore" -Value $gitignoreAdditions
Write-Host "  Added patterns to .gitignore" -ForegroundColor Gray

Write-Host ""
Write-Host "Step 3: Creating sample data directory..." -ForegroundColor Yellow
$sampleDir = "backend/test-data"
if (-not (Test-Path $sampleDir)) {
    New-Item -ItemType Directory -Path $sampleDir -Force | Out-Null
    Write-Host "  Created: $sampleDir" -ForegroundColor Gray
}

# Create a .gitkeep file
"# Test data files go here (not committed to Git)" | Out-File -FilePath "$sampleDir/.gitkeep" -Encoding utf8
Write-Host "  Created: $sampleDir/.gitkeep" -ForegroundColor Gray

Write-Host ""
Write-Host "Step 4: Committing changes..." -ForegroundColor Yellow
git add .gitignore
git add $sampleDir/.gitkeep
git commit -m "chore: remove test data files and update gitignore

- Remove CAS test/demo files from repository
- Add patterns to ignore test data files
- Create test-data directory for local testing" -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Changes committed successfully" -ForegroundColor Green
} else {
    Write-Host "  No changes to commit (files may already be removed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Push these changes: git push" -ForegroundColor White
Write-Host "2. To reduce GitHub repo size, run BFG Repo Cleaner (optional):" -ForegroundColor White
Write-Host "   - Download BFG: https://reps-protection.github.io/" -ForegroundColor Gray
Write-Host "   - Run: bfg --delete-files {acorns_*,cas_*}" -ForegroundColor Gray
Write-Host "   - Then: git reflog expire --expire=now --all" -ForegroundColor Gray
Write-Host "   - Then: git gc --prune=now --aggressive" -ForegroundColor Gray
Write-Host "   - Finally: git push --force" -ForegroundColor Gray
Write-Host ""
Write-Host "NOTE: Repo will still be ~375MB on GitHub until you clean history" -ForegroundColor Yellow
Write-Host "      But new clones after cleanup will be much smaller!" -ForegroundColor Yellow
Write-Host ""
