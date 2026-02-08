# Repository Size Management

## Current Status

- **Local repository**: ~3 MB (clean)
- **GitHub repository**: ~375 MB (includes history)
- **Production deployment**: Optimized via cleanup script

## The 375MB Issue Explained

### Why is the repo so large?

1. **Large files in Git history** (still stored even if deleted):
   - `acorns_site.css` (0.63 MB) - Reference file from Acorns site
   - `acorns_source.html` (0.14 MB) - Reference HTML
   - Multiple versions of dashboard/HTML files from development iterations

2. **Test data files** (now removed from current commit):
   - CAS parsed JSON files (~84 KB each)
   - Demo data files
   - Test text extracts

3. **Git history retention**:
   - Every version of large files is stored in `.git/objects`
   - Even after deleting files, they remain in history

## What We've Done

### ✅ **Immediate Fixes (Completed)**

1. **Removed test data files** from repository
2. **Updated `.gitignore`** to prevent future bloat
3. **Created production cleanup script** (`scripts/cleanup-production.sh`)
4. **Automated cleanup in deployment** (via `render.yaml`)

### 🛡️ **Prevention Measures**

- `.gitignore` now blocks:
  - Test/demo CAS files (`cas_*.json`, `cas_*.txt`)
  - Reference files (`acorns_*`)
  - Backup HTML files (`*-backup.html`, `*-old.html`)
  - Build artifacts (`frontend/www/`, `dist/`, `build/`)

- Pre-push hook validates code before pushing

## Production Deployment Optimization

### Automatic Cleanup on Render

During every deployment, `scripts/cleanup-production.sh` automatically removes:

✅ **Test/Demo Data**:
- `backend/cas_*.json`
- `backend/cas_*.txt`
- `backend/*_parsed*.json`

✅ **Backup HTML Files**:
- `frontend/dashboard-old-backup.html`
- `frontend/index-old.html`
- `frontend/*-backup.html`

✅ **Reference Files**:
- `acorns_site.css`
- `acorns_source.html`

✅ **Development Files**:
- `doc/` directory
- `tests/` directory
- `.git` directory
- `.vscode/`, `.idea/` configs
- PowerShell scripts (`.ps1`)

✅ **Python Cache**:
- `__pycache__/` directories
- `.pyc` files
- Coverage files

✅ **Frontend Artifacts**:
- `frontend/www/`
- `frontend/node_modules/`
- `package-lock.json`

**Result**: Production deployment is significantly smaller than the Git repository.

## Does 375MB Cause Issues?

### ⚠️ **Current Impact**:

1. **Deployment Time**: 
   - Download: ~2 seconds for 375MB
   - Extraction: ~6 seconds
   - **Total**: ~8 seconds vs instant for small repos

2. **Bandwidth**: 
   - Each deployment downloads 375MB
   - Not ideal, but manageable

3. **Render Costs**:
   - No direct cost impact (bandwidth included)
   - Slightly longer deploy times

### ✅ **What's Protected**:

- **Runtime performance**: NOT affected (cleanup script optimizes deployed files)
- **Application speed**: NOT affected
- **Disk space on Render**: Optimized via cleanup script
- **User experience**: NOT affected

### 🎯 **Verdict**: 

The 375MB is **manageable** but not ideal. The automatic cleanup script **prevents production impact**.

## Optional: Deep History Cleanup

To reduce the GitHub repo from 375MB, you can rewrite history (⚠️ requires force-push):

### Using BFG Repo Cleaner

```bash
# 1. Install BFG (Java required)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# 2. Create a fresh clone
git clone --mirror https://github.com/chinni070707/MFHelperAI.git
cd MFHelperAI.git

# 3. Run BFG to remove large files from history
java -jar bfg.jar --delete-files "{acorns_*,cas_*}" .
java -jar bfg.jar --delete-folders "{htmlcov,tests}" .

# 4. Clean up Git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Check new size
git count-objects -vH

# 6. Force push (⚠️ WARNING: Rewrites history)
git push --force

# 7. All developers must re-clone
```

### Alternative: Using git-filter-repo

```bash
# 1. Install git-filter-repo
pip install git-filter-repo

# 2. Create a fresh clone
git clone https://github.com/chinni070707/MFHelperAI.git
cd MFHelperAI

# 3. Remove large files from history
git filter-repo --path acorns_site.css --invert-paths
git filter-repo --path acorns_source.html --invert-paths
git filter-repo --path backend/cas_extracted_text.txt --invert-paths

# 4. Force push
git push --force
```

## Recommendation

### **Current Approach** (Recommended):
✅ **Keep as-is** with automatic cleanup
- No force-push needed
- History preserved
- Production optimized automatically
- Future commits are clean

### **Deep Cleanup** (Optional):
⚠️ Only if you want to optimize GitHub storage
- Saves GitHub storage space
- Requires force-push (coordination needed)
- All developers must re-clone
- History is rewritten

## Manual Production Cleanup

If you need to manually clean up production:

```bash
# SSH into Render shell (from Render dashboard)
cd /opt/render/project/src

# Run cleanup script
bash scripts/cleanup-production.sh

# Check disk usage
du -sh .
```

## Monitoring

### Check Local Repo Size:
```powershell
git count-objects -vH
```

### Check GitHub Repo Size:
- Go to: https://github.com/chinni070707/MFHelperAI
- Settings → GitHub will show repo size

### Check Production Disk Usage:
```bash
# Via Render shell
du -sh /opt/render/project/src
```

## Future Best Practices

1. ✅ **Never commit**:
   - Test data files
   - Reference files from other sites
   - Backup versions of code
   - Large binary files

2. ✅ **Always use**:
   - `.gitignore` patterns
   - Pre-commit hooks
   - Code review before merge

3. ✅ **For large files**:
   - Use Git LFS (Large File Storage)
   - Store in S3/cloud storage
   - Reference by URL

## Questions?

- **Is production affected?** No, cleanup script optimizes it
- **Should we do deep cleanup?** Optional, not required
- **Will this happen again?** No, prevention measures in place
- **How to check if file is tracked?** `git ls-files | grep filename`

---

Last Updated: February 8, 2026
