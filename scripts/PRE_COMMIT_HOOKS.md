# Pre-commit Hooks

This directory contains pre-commit hooks to ensure code quality and prevent broken code from being committed.

## What Gets Checked

Before every commit, the following checks are automatically run:

1. **Database Connection Test** - Validates database connectivity and schema
2. **Backend Unit Tests** - Runs all backend pytest tests
3. **Python Syntax Check** - Validates Python syntax for staged files

## Setup

### Windows (PowerShell)

```powershell
.\scripts\setup-pre-commit.ps1
```

### Linux/Mac (Bash)

```bash
bash scripts/setup-pre-commit.sh
```

## Testing the Hook

To test the pre-commit hook without committing:

### Windows
```powershell
powershell -ExecutionPolicy Bypass -File scripts\pre-commit-hook.ps1
```

### Linux/Mac
```bash
bash scripts/pre-commit-hook.sh
```

## Skipping the Hook

**Not recommended**, but if you need to bypass the hook:

```bash
git commit --no-verify
```

## Using Pre-commit Framework (Optional)

For more advanced configuration, you can use the [pre-commit framework](https://pre-commit.com/):

### Installation

```bash
pip install pre-commit
```

### Setup

```bash
pre-commit install
```

### Run Manually

```bash
pre-commit run --all-files
```

## What Happens on Failure

If any check fails:
- ❌ The commit will be **blocked**
- 📝 You'll see **detailed error messages**
- 🔧 **Fix the issues** and try committing again

## Benefits

✅ **Catch errors early** - Before they reach the server  
✅ **Faster feedback** - Know immediately if something breaks  
✅ **Cleaner history** - Only working code gets committed  
✅ **CI/CD friendly** - Fewer failed builds on GitHub Actions/Render  

## Troubleshooting

### Hook not running
- Ensure you ran the setup script
- Check that `.git/hooks/pre-commit` exists and is executable

### Tests failing locally
- Ensure database is running: `docker compose up -d`
- Install dependencies: `pip install -r backend/requirements.txt`
- Run tests manually to debug: `cd backend && pytest tests/ -v`

### Slow commits
- The hook runs all tests, which may take 10-30 seconds
- This is normal and ensures quality
- You can temporarily skip with `--no-verify` if urgent
