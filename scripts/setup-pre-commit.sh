#!/bin/bash
# Setup Pre-commit Hook (Bash)
# This script installs the pre-commit hook to run tests before every commit

echo ""
echo "🔧 Setting up pre-commit hook..."
echo ""

HOOK_PATH=".git/hooks/pre-commit"
SCRIPT_PATH="scripts/pre-commit-hook.sh"

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository. Please run this from the project root."
    echo ""
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy the pre-commit hook
cp "$SCRIPT_PATH" "$HOOK_PATH"
chmod +x "$HOOK_PATH"

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "The following checks will run before each commit:"
echo "  • Database connection test"
echo "  • Backend unit tests"
echo "  • Python syntax validation"
echo ""
echo "To skip the hook (not recommended), use:"
echo "  git commit --no-verify"
echo ""
echo "To test the hook now, run:"
echo "  ./$SCRIPT_PATH"
echo ""
