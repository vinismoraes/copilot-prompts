# Copilot Prompts

A curated, generic-first set of VS Code Copilot instruction files and reusable prompts for backend development, with optional packs for organization-specific workflows.

## Quick start

```bash
git clone git@github.com:vinismoraes/copilot-prompts.git ~/GoProjects/copilot-prompts
cd ~/GoProjects/copilot-prompts && ./scripts/install.sh
```

This installs the generic core profile by default. Restart VS Code and Copilot will start following the installed instructions.

## Why?

Out of the box, Copilot doesn't know your team's conventions. It will generate code that compiles but doesn't match your style, skip linters, forget commit message formats, and push without asking.

These instruction files fix that by giving Copilot persistent context about how you work:

**Without instructions:**
> You: "commit this"
>
> Copilot: runs `git commit -m "Updated the handler to fix the bug in the processing logic"` and pushes immediately

**With instructions:**
> You: "commit this"
>
> Copilot: "Here are the changes — ready to commit and push?"
>
> `fix request validation in handler`
>
> *(waits for confirmation, runs linters first, uses imperative mood, stays under 72 chars)*

The same pattern applies across the board — PR creation, code reviews, diagram formatting, testing conventions, and more.

## What's inside

| Folder | Type | Purpose |
|---|---|---|
| `instructions/core/` | `.instructions.md` | Generic always-on rules installed by default |
| `instructions/league/` | `.instructions.md` | Optional organization-specific instruction pack (example pack) |
| `prompts/core/` | `.prompt.md` | Generic reusable task prompts installed by default |
| `prompts/league/` | `.prompt.md` | Optional organization-specific prompts (example pack) |
| `scripts/` | `.sh` | Task workflow scripts (worktrees, install) + install script |

### Instructions

| File | Applies to | Description |
|---|---|---|
| `diagrams.instructions.md` | `**` | Use Mermaid syntax for all diagrams and flowcharts |
| `git-commits.instructions.md` | `**` | One-line, imperative, lowercase commit messages under 72 chars |
| `git-push.instructions.md` | `**` | Always ask for confirmation before committing or pushing |
| `go-standards.instructions.md` | `**/*.go` | Go coding standards — formatting, testing, mocking, comments |
| `pr-creation.instructions.md` | `**` | Always create PRs as draft, include issue tracker link |
| `pr-reviews.instructions.md` | `**` | Explain PR feedback before acting, wait for user approval |
| `pre-commit-lint.instructions.md` | `**/*.go` | Run local linters before every commit |
| `task-workflow.instructions.md` | `**` | Multi-repo worktree management for cross-repo tasks |

### Optional organization pack (league example)

These files are available but not installed in the default core profile:

| File | Applies to | Description |
|---|---|---|
| `circleci.instructions.md` | `**` | CircleCI API interaction for checking CI status and rerunning jobs |
| `locale-ignore.instructions.md` | `src/el/**/*.go` | Add `// locale.Ignore` comments to non-user-facing strings |
| `mcp-tools.instructions.md` | `**/mcp/**/*.go` | MCP tool development patterns for messaging and connected care |
| `mirrord.instructions.md` | `**` | Running services locally with mirrord against remote envs |

### Prompts

| File | Description |
|---|---|
| `quick-start-repo.prompt.md` | Bootstrap a new local Go repo and start a task workspace |
| `mirrord.prompt.md` | Run mirrord to test a local app against a remote environment (optional profile) |

### Scripts

| File | Description |
|---|---|
| `install.sh` | Symlinks prompts into VS Code and task scripts into `$REPOS_ROOT` |
| `quick-start-repo.sh` | Creates a local Go repo scaffold (`main`, `go.mod`, `main.go`) |
| `new-task.sh` | Start a new multi-repo task — creates worktrees, generates a `.code-workspace`, opens VS Code |
| `add-repo.sh` | Add a repo to an existing task mid-flight |
| `done-task.sh` | Clean up worktrees and workspace when a task is done |

Multi-repo task workflow is documented in this README and in `instructions/core/task-workflow.instructions.md`.

## Setup

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) and [GitHub Copilot Chat](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) extensions installed

### Option 1: Install script (recommended)

Clone the repo and run the install script to symlink all files into VS Code's prompt directory:

```bash
git clone git@github.com:vinismoraes/copilot-prompts.git ~/GoProjects/copilot-prompts
cd ~/GoProjects/copilot-prompts
./scripts/install.sh
```

Install profiles:

```bash
# Generic core profile (default)
./scripts/install.sh --profile core

# Core + optional organization pack
./scripts/install.sh --profile league

# Install everything found in instructions/ and prompts/
./scripts/install.sh --profile all
```

Optional pruning:

```bash
# Remove repo-managed links not selected by profile
./scripts/install.sh --profile core --prune
```

The script creates symlinks from your VS Code prompts directory to this repo, so pulling updates automatically applies them. It also symlinks the task workflow scripts (`new-task.sh`, `add-repo.sh`, `done-task.sh`, `quick-start-repo.sh`) into `$REPOS_ROOT` (default: `~/GoProjects`) and validates they are callable from your shell.

If `$REPOS_ROOT` is not in `PATH`, install automatically appends it to your shell rc file (for example `~/.zshrc`).

```bash
# Skip shell PATH updates if you prefer managing PATH manually
./scripts/install.sh --no-shell-path
```

### Option 2: Manual copy

Copy the files directly into your VS Code user prompts folder:

```bash
# macOS
PROMPTS_DIR=~/Library/Application\ Support/Code/User/prompts
mkdir -p "$PROMPTS_DIR"
cp instructions/core/*.instructions.md "$PROMPTS_DIR/"
cp prompts/core/*.prompt.md "$PROMPTS_DIR/"

# Optional organization pack
cp instructions/league/*.instructions.md "$PROMPTS_DIR/"
cp prompts/league/*.prompt.md "$PROMPTS_DIR/"
```

> **Note:** With manual copy you'll need to re-copy files after pulling updates.

## How it works

VS Code Copilot loads `.instructions.md` files from `~/Library/Application Support/Code/User/prompts/` (macOS) automatically. Each file has YAML frontmatter that controls when it activates:

```yaml
---
applyTo: "**/*.go"           # glob pattern — when working on matching files
description: Short summary   # shown in VS Code settings UI
---
```

- `applyTo: "**"` — active for all files (always-on)
- `applyTo: "**/*.go"` — active only when working on Go files
- `applyTo: "src/**/*.go"` — active only for Go files under `src/`

`.prompt.md` files are reusable task prompts you can invoke from the Copilot Chat panel. They appear in the prompt picker when you type `/`.

## Updating

```bash
cd ~/GoProjects/copilot-prompts
git pull
```

If you used the install script (symlinks), changes apply immediately. If you copied manually, re-run the copy commands.

## Contributing

To propose a new prompt or modify an existing one:

1. Fork this repository
2. Create a new `.instructions.md` or `.prompt.md` file in the appropriate folder (or edit an existing one)
3. Include YAML frontmatter with `applyTo` and `description` fields:
   ```yaml
   ---
   applyTo: "**/*.go"
   description: Short description of what this instruction does
   ---
   ```
4. Open a pull request with a clear description of the change

### Guidelines

- **Instructions** (`instructions/core/`, `instructions/league/`): Always-on rules that activate based on file patterns. Use core for generic behavior and optional packs for organization-specific behavior.
- **Prompts** (`prompts/core/`, `prompts/league/`): On-demand task templates invoked from the Copilot Chat panel. Keep generic and organization-specific prompts separated.
- **Scripts** (`scripts/`): Shell scripts referenced by instructions or prompts. Keep them portable across macOS and Linux.
- Keep instruction files focused on a single concern — prefer multiple small files over one large file.
- Test new prompts locally before submitting by copying them to your VS Code prompts directory.

## License

MIT — use it, fork it, adapt it to your own team's conventions.
