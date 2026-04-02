---
applyTo: "**"
description: Multi-repo worktree task management — auto-setup workspaces for cross-repo work
---

# Multi-Repo Task Workflow

Scripts manage git worktrees and VS Code multi-root workspaces for cross-repo tasks.
The repo root is configured via the `REPOS_ROOT` env var (default: `~/GoProjects`).

## Starting a new task

When the user says they are starting a new task or mentions a branch name (e.g. `PCHAT-1234`, `add-search`):

1. Ask which repos the task involves.
2. Run the setup script:

```bash
./new-task.sh my-feature repo-a repo-b
```

3. This creates worktrees on a new branch, generates a `.code-workspace`, and opens VS Code with all repos as roots.
4. Before starting, check for stale worktrees from previous tasks and offer to clean them up.

## Adding a repo mid-task

If the task expands to touch another repo:

```bash
./add-repo.sh my-feature repo-c
```

## Finishing a task

When the user says they're done with a task (regardless of PR status — PRs may be open, merged, or not created yet), offer to clean up:

1. Run the cleanup script **first** (as a background terminal — the user will close the window after):

```bash
./done-task.sh my-feature
```

2. Once cleanup succeeds, give the user a short send-off and tell them it's safe to close the window. Keep it human — something like:

> All clean. You're good to close this window. ✌️

This removes the worktrees and workspace directory. Remote branches stay intact.

**Important**: Run `done-task.sh` as a **background** terminal (`isBackground: true`) so it executes even if the user closes the window shortly after. Do NOT ask the user to close the window first — that kills the agent before cleanup can run.

## Available repos

Repos live under `$REPOS_ROOT/`.

## Important

- Always confirm the branch name and repos before running `new-task.sh`
- The `services` repo automatically gets `src/el` added as a second workspace root when present
- Worktrees are created at `$REPOS_ROOT/worktrees/BRANCH/`
- Main clones at `$REPOS_ROOT/` are never modified
- When a task is done, run `done-task.sh` as a background terminal, then tell the user to close the window
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
./new-task.sh my-feature REPO_NAME
```

This creates an initial `main` branch and commit, then creates the task worktree/branch and workspace.
