---
applyTo: "**/*.go"
description: Run local linters before every commit to catch CI failures early
---

# Pre-Commit Linting

Before committing Go code in the `services` repo, **always run the local linter script** on changed files:

```bash
~/GoProjects/scripts/lint-services.sh --changed
```

This runs the same checks as the CI `linters` job (gofmt, goimports, revive, misspell, gofix, blocklist) but only on files changed vs `origin/main`.

## Workflow

1. After making code changes and before proposing a commit, run:
   ```bash
   ~/GoProjects/scripts/lint-services.sh --changed
   ```
2. If any linter fails, **fix the issues before committing**
3. Only propose the commit once all linters pass

## Fixing common failures

- **gofmt**: Run `gofmt -s -w <file>` to auto-fix
- **goimports**: Run `goimports -w <file>` to auto-fix
- **revive**: Read the error message and fix the code pattern
- **misspell**: Fix the typo in the source
- **blocklist**: Remove the forbidden pattern (see error message for alternatives)

## Running specific linters

```bash
~/GoProjects/scripts/lint-services.sh --changed gofmt goimports  # only these two
~/GoProjects/scripts/lint-services.sh gofmt                       # full repo, one linter
```
