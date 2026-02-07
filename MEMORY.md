# Memory - User Preferences & Project Rules

## Workflow Rules

- **Always run tests before commit** - Run `pytest tests/ -v` (backend) and/or Playwright tests before any git commit
- **No unicode characters in code** - Do not use unicode symbols, emojis, or special characters in source code files
- **Debug mode for debugging** - When debugging the application, run it in debug mode (`DEBUG=true` or `.\startup.ps1` with dev settings)

## Development Preferences

- Windows development environment (PowerShell scripts preferred)
- Use `.\startup.ps1` for starting the full dev stack
- Pre-push hooks should always be active for code quality
- Prefer specific `git add <file>` over `git add -A`

## Project Context

- Target audience: Indian mutual fund investors
- Design system: Acorns-inspired green palette (#7FC04C)
- AI integration: Ollama local-first, OpenAI as fallback
- PWA-capable with offline support via Service Worker

## Testing Checklist (Before Commit)

1. Backend: `cd backend && pytest tests/ -v`
2. Type check: `cd frontend && npm run type-check`
3. E2E (if UI changed): `cd tests && npx playwright test`
4. Pre-push validation: `.\pre-push-check.ps1`
