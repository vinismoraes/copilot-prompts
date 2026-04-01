---
applyTo: "**"
description: Multi-repo worktree task management — auto-setup workspaces for cross-repo work
---

# Multi-Repo Task Workflow

Scripts manage git worktrees and VS Code multi-root workspaces for cross-repo tasks.
The repo root is configured via the `REPOS_ROOT` env var (default: `~/GoProjects`).

## Starting a new task

When the user says they are starting a new task or mentions a ticket number (e.g. `TASK-1234`):

1. Ask which repos the task involves.
2. Run the setup script:

```bash
./new-task.sh TICKET-1234 repo-a repo-b
```

3. This creates worktrees on a new branch, generates a `.code-workspace`, and opens VS Code with all repos as roots.
4. Before starting, check for stale worktrees from previous tasks and offer to clean them up.

## Adding a repo mid-task

If the task expands to touch another repo:

```bash
./add-repo.sh TICKET-1234 repo-c
```

## Finishing a task

When the user says they're done with a task (regardless of PR status — PRs may be open, merged, or not created yet), offer to clean up:

1. Close the VS Code worktree window first (it will become invalid after cleanup)
2. Run the cleanup script:

```bash
./done-task.sh TICKET-1234
```

This removes the worktrees and workspace directory. Remote branches stay intact.

**Reminder**: Always close the worktree VS Code window before running `done-task.sh` — leaving stale windows open causes confusion and workspace errors.

## Available repos

Repos live under `$REPOS_ROOT/`.

## Important

- Always confirm the ticket number and repos before running `new-task.sh`
- The `services` repo automatically gets `src/el` added as a second workspace root when present
- Worktrees are created at `$REPOS_ROOT/worktrees/TICKET/`
- Main clones at `$REPOS_ROOT/` are never modified
- Main clones at `$REPOS_ROOT/` are never modified
- When a task is done, **close the worktree VS Code window** before running `done-task.sh` to avoid stale workspace errors
- If you notice orphaned worktree windows (workspace files that no longer exist), close them immediately

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
