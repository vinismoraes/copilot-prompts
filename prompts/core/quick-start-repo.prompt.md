---
description: Quick start a new local Go repo and open a task workspace
---

# Quick Start Repo

Bootstraps a brand-new local Go repository and starts a task workspace for it.

Collect these inputs from the user before running commands:
- `BRANCH` (for example, `PCHAT-1001` or `my-feature`)
- `REPO_NAME` (folder name under `$REPOS_ROOT`, default `~/GoProjects`)
- Optional `MODULE_PATH` (default: `example.com/<repo_name>`)

## Steps

1. Create the repository scaffold:

```bash
~/GoProjects/quick-start-repo.sh REPO_NAME --module MODULE_PATH
```

If `MODULE_PATH` is not provided, run:

```bash
~/GoProjects/quick-start-repo.sh REPO_NAME
```

2. Create and open the task workspace:

```bash
~/GoProjects/new-task.sh BRANCH REPO_NAME
```

3. Report back with:
- repo path
- workspace path
- next suggested command (`code --new-window <workspace_file>` if VS Code did not open)
