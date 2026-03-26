# Copilot Prompts

Custom VS Code Copilot instruction and prompt files for Go backend development in the League services repo.

## What's inside

| Folder | Type | Purpose |
|---|---|---|
| `instructions/` | `.instructions.md` | Always-on rules Copilot follows automatically based on `applyTo` glob patterns |
| `prompts/` | `.prompt.md` | Reusable task prompts you invoke on demand (e.g. "run mirrord") |
| `scripts/` | `.sh` | Task workflow scripts (worktrees, install) + install script |

### Instructions

| File | Applies to | Description |
|---|---|---|
| `circleci.instructions.md` | `**` | CircleCI API interaction for checking CI status and rerunning jobs |
| `diagrams.instructions.md` | `**` | Use Mermaid syntax for all diagrams and flowcharts |
| `git-commits.instructions.md` | `**` | One-line, imperative, lowercase commit messages under 72 chars |
| `git-push.instructions.md` | `**` | Always ask for confirmation before committing or pushing |
| `go-standards.instructions.md` | `**/*.go` | Go coding standards — formatting, testing, mocking, comments |
| `locale-ignore.instructions.md` | `src/el/**/*.go` | Add `// locale.Ignore` comments to non-user-facing strings |
| `mcp-tools.instructions.md` | `**/mcp/**/*.go` | MCP tool development patterns for messaging and connected care |
| `mirrord.instructions.md` | `**` | Running services locally with mirrord against remote envs |
| `pr-creation.instructions.md` | `**` | Always create PRs as draft, include Jira ticket link |
| `pr-reviews.instructions.md` | `**` | Explain PR feedback before acting, wait for user approval |
| `pre-commit-lint.instructions.md` | `**/*.go` | Run local linters before every commit |
| `task-workflow.instructions.md` | `**` | Multi-repo worktree management for cross-repo tasks |

### Prompts

| File | Description |
|---|---|
| `mirrord.prompt.md` | Run mirrord to test a local app against a remote environment |

### Scripts

| File | Description |
|---|---|
| `install.sh` | Symlinks prompts into VS Code and task scripts into `$REPOS_ROOT` |
| `new-task.sh` | Start a new multi-repo task — creates worktrees, generates a `.code-workspace`, opens VS Code |
| `add-repo.sh` | Add a repo to an existing task mid-flight |
| `done-task.sh` | Clean up worktrees and workspace when a task is done |

See the [multi-repo task workflow gist](https://gist.github.com/vinismoraes/e6ee5f8dfacb95571f44d13b2cb78476) for detailed documentation.

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

The script creates symlinks from your VS Code prompts directory to this repo, so pulling updates automatically applies them. It also symlinks the task workflow scripts (`new-task.sh`, `add-repo.sh`, `done-task.sh`) into `$REPOS_ROOT` (default: `~/GoProjects`).

### Option 2: Manual copy

Copy the files directly into your VS Code user prompts folder:

```bash
# macOS
PROMPTS_DIR=~/Library/Application\ Support/Code/User/prompts
mkdir -p "$PROMPTS_DIR"
cp instructions/*.instructions.md "$PROMPTS_DIR/"
cp prompts/*.prompt.md "$PROMPTS_DIR/"
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
- `applyTo: "src/el/**/*.go"` — active only for Go files under `src/el/`

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

- **Instructions** (`instructions/`): Always-on rules that activate based on file patterns. Use these for coding standards, security policies, and workflow conventions.
- **Prompts** (`prompts/`): On-demand task templates invoked from the Copilot Chat panel. Use these for repeatable multi-step workflows.
- **Scripts** (`scripts/`): Shell scripts referenced by instructions or prompts. Keep them portable across macOS and Linux.
- Keep instruction files focused on a single concern — prefer multiple small files over one large file.
- Test new prompts locally before submitting by copying them to your VS Code prompts directory.
