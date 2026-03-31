---
applyTo: "**"
description: Multi-repo worktree task management — auto-setup workspaces for cross-repo work
---

# Multi-Repo Task Workflow

Scripts manage git worktrees and VS Code multi-root workspaces for cross-repo tasks.
The repo root is configured via the `REPOS_ROOT` env var (default: `~/GoProjects`).

## Starting a new task

When the user says they're starting a new task or mentions a ticket number (e.g. PCHAT-1234):

1. Ask which repos the task involves (default: `services`)
2. Run the setup script:

```bash
./new-task.sh TICKET-1234 services backend-extensions
```

3. This creates worktrees on a new branch, generates a `.code-workspace`, and opens VS Code with all repos as roots.

## Adding a repo mid-task

If the task expands to touch another repo:

```bash
./add-repo.sh TICKET-1234 api-specs
```

## Finishing a task

When all PRs for a task are merged, the task is done. Offer to clean up:

```bash
./done-task.sh TICKET-1234
```

This removes the worktrees and workspace directory. Remote branches stay intact.

## Available repos

Repos live under `$REPOS_ROOT/`. Common ones:
- `services` — main backend monolith (Go)
- `backend-extensions` — backend extensions (Go)
- `api-specs` — OpenAPI specs
- `protobuf` — proto definitions

## Important

- Always confirm the ticket number and repos before running `new-task.sh`
- The `services` repo automatically gets `src/el` added as a second workspace root
- Worktrees are created at `$REPOS_ROOT/worktrees/TICKET/`
- Main clones at `$REPOS_ROOT/` are never modified

## Quick starting a new repo

If the task requires a brand-new repo that does not exist under `$REPOS_ROOT`:

1. Ask for repo name and optional Go module path.
2. Bootstrap the repo:

```bash
./quick-start-repo.sh REPO_NAME --module example.com/REPO_NAME
```

3. Start the task with that repo:

```bash
./new-task.sh TICKET-1234 REPO_NAME
```

This creates an initial `main` branch and commit, then creates the task worktree/branch and workspace.
