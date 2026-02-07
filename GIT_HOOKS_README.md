# Git Hooks and Pre-Push Validation

Automated code validation that runs before every `git push`.

## 🚀 Quick Setup

**Install the pre-push hook (one-time setup):**
```powershell
.\install-git-hooks.ps1
```

This will automatically run validation checks before every push!

## ✅ What Gets Checked

### 1. **Python Syntax Validation**
   - Compiles all Python files to check for syntax errors
   - Catches typos, missing imports, etc.

### 2. **Import Validation**
   - Tests if core modules (`app.config`, `app.main`) can be imported
   - Prevents pushing broken imports

### 3. **Common Issues Detection**
   - Print statements without `file=` parameter (encoding issues)
   - Hardcoded localhost URLs in config
   - Other production-ready checks

### 4. **Requirements Check**
   - Verifies all critical packages are in `requirements.txt`
   - Ensures: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic

### 5. **Deployment Files**
   - Checks that `render.yaml`, `build.sh`, `.renderignore` exist

## 🎯 Usage

### Automatic (Recommended)
After installation, validation runs automatically on every `git push`:
```powershell
git push origin main
# Hook runs validation...
# ✅ Push succeeds if all checks pass
# ❌ Push blocked if checks fail
```

### Manual Run
Run validation anytime without pushing:
```powershell
.\pre-push-check.ps1
```

### Bypass Hook (Emergency Only)
Skip validation (NOT recommended):
```powershell
git push --no-verify
```

## 📊 Example Output

```
🔍 Running pre-push validation checks...

📝 Checking Python syntax...
  ✅ All Python files have valid syntax (45 files checked)

📦 Validating Python imports...
  ✅ Core imports validated successfully

🔎 Checking for common issues...
  ✅ No common issues detected

📋 Checking requirements.txt...
  ✅ All critical packages present in requirements.txt

🚀 Checking deployment files...
  ✅ All deployment files present

==================================================
✅ ALL CHECKS PASSED!
Safe to push to Git.
==================================================
```

## 🔧 Customization

Edit `pre-push-check.ps1` to add your own checks:
- Add more linting rules
- Check code formatting
- Run quick unit tests
- Validate environment files

## 🐛 Troubleshooting

**Hook not running?**
- Verify: `Test-Path .git\hooks\pre-push` returns `True`
- Re-run: `.\install-git-hooks.ps1`

**Validation fails locally?**
- Run: `.\pre-push-check.ps1` to see detailed errors
- Fix reported issues
- Try push again

**Need to push urgently despite errors?**
- Use: `git push --no-verify` (fix issues after!)

## 📝 Files

- `pre-push-check.ps1` - Validation script
- `install-git-hooks.ps1` - One-time installer
- `.git/hooks/pre-push` - Git hook (auto-created)

## 🎨 Benefits

✅ **Catch errors early** - Before they reach production
✅ **Faster development** - No more "oops, broke the build"
✅ **Team consistency** - Everyone runs same checks
✅ **Production safety** - Prevents common deployment issues
✅ **Zero overhead** - Only runs when pushing

---

**Happy coding! Your code is now protected by automated validation.** 🛡️
