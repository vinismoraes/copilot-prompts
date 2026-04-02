# Copilot Prompts

A curated set of [VS Code Copilot instruction files](https://code.visualstudio.com/docs/copilot/copilot-customization) and reusable prompts for backend development. Generic-first, with optional packs for organization-specific workflows.

## Quick start

```bash
git clone git@github.com:vinismoraes/copilot-prompts.git ~/GoProjects/copilot-prompts
cd ~/GoProjects/copilot-prompts && ./scripts/install.sh
```

This installs the **core** profile by default. Restart VS Code and Copilot will start following the installed instructions.

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

```
copilot-prompts/
├── instructions/
│   ├── core/           # Generic always-on rules (installed by default)
│   └── league/         # Organization-specific pack (example, opt-in)
├── prompts/
│   ├── core/           # Generic reusable task prompts (installed by default)
│   └── league/         # Organization-specific prompts (opt-in)
└── scripts/            # Install script + task workflow scripts
```

### Core instructions (installed by default)

| File | Applies to | What it does |
|---|---|---|
| `diagrams.instructions.md` | `**` | Use Mermaid syntax for all diagrams and flowcharts |
| `git-commits.instructions.md` | `**` | One-line, imperative, lowercase commit messages under 72 chars |
| `git-push.instructions.md` | `**` | Always ask for confirmation before committing or pushing |
| `go-standards.instructions.md` | `**/*.go` | Go coding standards — formatting, testing, mocking, comments |
| `pr-comments.instructions.md` | `**` | Positive, concise PR comments — always confirm before posting |
| `pr-creation.instructions.md` | `**` | Always create PRs as draft, include issue tracker link |
| `pr-reviews.instructions.md` | `**` | Explain PR feedback before acting, wait for user approval |
| `task-workflow.instructions.md` | `**` | Multi-repo worktree management for cross-repo tasks |

### Organization pack (league example, opt-in)

Install with `./scripts/install.sh --profile league`. These layer on top of core:

| File | Applies to | What it does |
|---|---|---|
| `circleci.instructions.md` | `**` | CircleCI API interaction for CI status and rerunning jobs |
| `league-security-policy.instructions.md` | `**` | HIPAA platform security guardrails |
| `locale-ignore.instructions.md` | `src/el/**/*.go` | Add `// locale.Ignore` to non-user-facing strings |
| `mcp-tools.instructions.md` | `**/mcp/**/*.go` | MCP tool development patterns |
| `mirrord.instructions.md` | `**` | Running services locally with mirrord against remote envs |
| `pre-commit-lint.instructions.md` | `**/*.go` | Run local linters before every commit |
| `pr-creation.instructions.md` | `**` | PR creation with Jira ticket conventions (overrides core) |
| `pr-reviews.instructions.md` | `**` | PR reviews with Copilot reviewer bot (overrides core) |

### Prompts

| File | Profile | What it does |
|---|---|---|
| `quick-start-repo.prompt.md` | core | Bootstrap a new local Go repo and start a task workspace |
| `mirrord.prompt.md` | league | Run mirrord to test a local app against a remote environment |

### Scripts

| Script | What it does |
|---|---|
| `install.sh` | Symlinks prompts into VS Code and task scripts into `$REPOS_ROOT` |
| `new-task.sh` | Start a multi-repo task — creates worktrees, `.code-workspace`, opens VS Code |
| `add-repo.sh` | Add a repo to an existing task mid-flight |
| `done-task.sh` | Clean up worktrees and workspace when a task is done |
| `quick-start-repo.sh` | Create a local Go repo scaffold (`main`, `go.mod`, `main.go`) |

## Setup

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) extension
- macOS or Linux

### Option 1: Install script (recommended)

```bash
git clone git@github.com:vinismoraes/copilot-prompts.git ~/GoProjects/copilot-prompts
cd ~/GoProjects/copilot-prompts
./scripts/install.sh
```

**Profiles** control which instruction packs get installed:

```bash
./scripts/install.sh                    # core only (default)
./scripts/install.sh --profile league   # core + league pack
./scripts/install.sh --profile all      # everything
```

**Pruning** removes symlinks from previous profiles that are no longer selected:

```bash
./scripts/install.sh --profile core --prune
```

The script symlinks files from your VS Code prompts directory to this repo — pulling updates applies them immediately. Task workflow scripts (`new-task.sh`, `add-repo.sh`, `done-task.sh`, `quick-start-repo.sh`) are symlinked into `$REPOS_ROOT` (default: `~/GoProjects`).

If `$REPOS_ROOT` is not in `PATH`, install appends it to your shell rc file. Skip with `--no-shell-path`.

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

1. Fork this repo
2. Add or edit files in the appropriate folder
3. Include YAML frontmatter:
   ```yaml
   ---
   applyTo: "**/*.go"
   description: Short description of what this instruction does
   ---
   ```
4. Open a pull request

### Creating your own pack

To add an organization-specific pack (e.g. `acme`):

1. Create `instructions/acme/` and/or `prompts/acme/`
2. Add your `.instructions.md` and `.prompt.md` files
3. Install with `./scripts/install.sh --profile acme` (the `all` profile picks up new packs automatically)

If a pack file has the same name as a core file (e.g. `pr-creation.instructions.md`), the pack version overrides core — the last symlink wins.

### Guidelines

- One concern per file — prefer multiple small files over one large file
- Use `instructions/` for always-on rules (activated by `applyTo` globs)
- Use `prompts/` for on-demand tasks (invoked from the Copilot Chat panel via `/`)
- Keep scripts portable across macOS and Linux

## License

MIT — use it, fork it, adapt it to your own team's conventions.
