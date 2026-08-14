---
applyTo: "**"
description: eos CLI usage for local dev environment orchestration
---

# eos CLI

`eos` orchestrates the local development environment — connecting backend services via mirrord and starting client platforms (web/android/ios) against League test environments.

## Key constraint

- **Always use explicit flags** — never rely on the interactive wizard (it blocks on stdin)
- Add `--no-open` for web to prevent browser pop-ups
- Use `--dry-run --json` to inspect resolved config without launching processes

## Commands

### Start environment

```bash
# Full stack: backend + client
eos start -e test2-ca -P chat -p web --no-open

# Backend only
eos start -e test2-ca -s messaging --no-client

# Multiple services
eos start -e test2-ca -s messaging,api --no-client

# Profile + add/remove services
eos start -P chat -s +api          # add api to profile
eos start -P chat -s -connected_care  # remove from profile

# Dry-run (JSON output, no execution)
eos start -e test2-ca -P chat --dry-run --json
```

Flags: `-e` env, `-p` platform (web|android|ios|none), `-s` services, `-P` profile, `-r` route, `--no-client`, `--no-backend`, `--no-detect`, `--port`, `--no-open`, `--dry-run`, `--json`

### Deploy to test environment

```bash
eos deploy -e test2-ca -s messaging       # deploy service
eos deploy -e test2-ca                     # deploy auto-detected
eos deploy --status -e test2-ca            # show current tags (read-only)
eos deploy --find-env                      # find available env
eos deploy --revert -s messaging -e test2-ca  # reset to main
eos deploy --dry-run -e test2-ca -s messaging # preview
```

### Status and diagnostics

```bash
eos status    # tool availability, kubectl context, mirrord sessions
eos doctor    # deep check: auth, certs, repos, mirrord operator
```

### Profiles

```bash
eos profiles list
eos profiles show chat
```

### Other

```bash
eos accounts   # demo credentials info
eos config show
eos config set defaults.env test2-ca
```

## Available environments

test1-ca, test2-ca, test3-ca, test4-ca, test5-ca, test1-au, test2-au, test3-au

## Available services

messaging, services, api, benefits, claims, care_finder, connected_care, content_authoring, dynamic_questionnaire

## Built-in profiles

chat, benefits, content, backend-only

## Important

- `eos start` runs in the foreground — use an async terminal (it stays running until Ctrl-C)
- Only test environments are accepted — production/staging names are rejected
- Auto-detection picks services from `git diff` on feature branches (disable with `--no-detect`)
- The route defaults to the user's git email prefix for mirrord traffic isolation
