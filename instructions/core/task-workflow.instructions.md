---
applyTo: "**"
description: Multi-repo worktree task management — auto-setup workspaces for cross-repo work
---

# Multi-Repo Task Workflow

Scripts manage git worktrees and VS Code multi-root workspaces for cross-repo tasks.
The repo root is configured via the `REPOS_ROOT` env var (default: `~/GoProjects`).

## Starting a new task

When the user says they are starting a new task or mentions a branch name (e.g. `PCHAT-1234`, `add-search`):

1. Ask (or infer from the ticket) which repos the task involves.
2. **Decide whether task-scoping is worth it**:
   - If the task touches only the user's default repo (backend devs: `services`) → **skip `new-task.sh`**, just work on a branch in the existing checkout. The scoped workspace adds friction with no measurable benefit here.
   - If the task touches any repo outside the user's default (backend-extensions, agent-orchestrator, kubernetes-migration, eos-apps, etc.) → **run `new-task.sh`** so the workspace narrows to only the relevant repos.
3. If step 2 chose scoping, run the setup script:

```bash
./new-task.sh my-feature repo-a repo-b
```

4. This creates worktrees on a new branch, generates a `.code-workspace`, writes/verifies the Obsidian project note, and opens VS Code with all repos as roots. When skipping the workspace script, create/update and verify the project note using `task-journal.py start` if a vault is configured.
5. Before starting, check for stale worktrees from previous tasks and offer to clean them up.

*(Rationale: internal Week 1 study, July 2026, N=8 tickets, 25 Claude Code runs. Task-scoping produced +50–100pp first-attempt file coverage when the target repo was outside the user's default, and 0pp difference — dominated by ~27pp model non-determinism — for same-default-repo tickets. Full data: `~/GoProjects/studies/task-scoped-agent-context/runs/_summary.md`.)*

## Adding a repo mid-task

If the task expands to touch another repo:

```bash
./add-repo.sh my-feature repo-c
```

## Finishing a task

When the user says they're done with a task (regardless of PR status), record and verify completion before giving the final response. This applies even when no task workspace was created or the user keeps it open. If an Obsidian vault is configured, load `obsidian-journaling.instructions.md` and run:

```bash
python3 "${REPOS_ROOT:-$HOME/GoProjects}/task-journal.py" finish my-feature --summary "One factual sentence about the outcome."
python3 "${REPOS_ROOT:-$HOME/GoProjects}/task-journal.py" verify my-feature --completed
```

This sets the project note to `DONE` and adds a linked entry to today's daily note. Verify actual PR links separately; user-confirmed task completion alone does not establish merge or deployment status. If journaling fails, preserve the workspace and report the failure. If the helper is missing, use the safe manual journaling procedure and read back both notes.

Offer workspace cleanup separately when a workspace exists. If cleanup is requested, run `./done-task.sh my-feature`; it journals and verifies before removing worktrees and the workspace directory. Remote branches stay intact. Do not use cleanup merely to write notes, and do not repeat a completion entry already recorded for today.

If the harness supports a background terminal, cleanup may use it, but wait for successful completion before saying it is safe to close the window.

## Absorbing latest `main` into an in-flight task

When the user asks to "rebase onto main", "sync with main", "pull in latest main", or similar for an active task, use `sync-task.sh`:

```bash
./sync-task.sh my-feature              # rebase (default)
./sync-task.sh my-feature --merge      # merge instead
./sync-task.sh my-feature --dry-run    # preview
```

For each worktree of the task: fetches origin, safely fast-forwards local `main`, then rebases (or merges) the task branch onto `origin/main`. Skips any worktree with uncommitted changes (warns) and aborts cleanly on conflicts (exits 2). Never touches WIP.

If it reports conflicts, don't retry blindly — surface the conflicted worktree path and let the user resolve manually.

## Keeping main clones fresh in the background

A launchd job (`~/Library/LaunchAgents/com.vinismoraes.sync-main-clones.plist`) runs `sync-main-clones.sh --quiet` every 30 min. It fetches every top-level clone under `$REPOS_ROOT` and safely updates local `main` via the shared `safe_update_main` helper — never desyncs a working tree, even when `main` is checked out in a VS Code window.

If a main clone is showing stale/phantom file changes, DON'T guess the fix — run `~/GoProjects/dev-workspace/clean-clones.sh --dry-run` first to see the state, and check `~/Library/Logs/sync-main-clones.log` for recent activity.

## Available repos

Repos live under `$REPOS_ROOT/`.

## Important

- Always confirm the branch name and repos before running `new-task.sh`
- The `services` repo automatically gets `src/el` added as a second workspace root when present
- Worktrees are created at `$REPOS_ROOT/worktrees/BRANCH/`
- Main clones at `$REPOS_ROOT/` are never modified
- When a task is done, record and verify its Obsidian completion; clean up the workspace only when requested
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
