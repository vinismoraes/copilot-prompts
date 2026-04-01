#!/bin/zsh
# Installs copilot prompts, task scripts, and the cleanup scheduler.
#
# Prompts:   symlinked into VS Code's user prompts directory
# Scripts:   symlinked into $REPOS_ROOT (default: ~/GoProjects)
# Scheduler: launchd agent to auto-cleanup merged task worktrees
#
# Re-running is safe — existing symlinks are skipped.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
REPOS_ROOT=${REPOS_ROOT:-~/GoProjects}

# --- Prompts ---

case "$(uname)" in
  Darwin) PROMPTS_DIR="$HOME/Library/Application Support/Code/User/prompts" ;;
  Linux)  PROMPTS_DIR="$HOME/.config/Code/User/prompts" ;;
  *)      echo "Unsupported OS"; exit 1 ;;
esac

mkdir -p "$PROMPTS_DIR"

echo "Installing prompts → $PROMPTS_DIR"
for f in "$REPO_DIR"/instructions/*.instructions.md; do
  name=$(basename "$f")
  target="$PROMPTS_DIR/$name"
  if [[ -L "$target" ]]; then
    echo "  ✓ $name (already linked)"
  elif [[ -f "$target" ]]; then
    echo "  ⚠️ $name exists (not a symlink) — skipping. Remove it manually to use the repo version."
  else
    ln -s "$f" "$target"
    echo "  ✓ $name"
  fi
done

for f in "$REPO_DIR"/prompts/*.prompt.md; do
  name=$(basename "$f")
  target="$PROMPTS_DIR/$name"
  if [[ -L "$target" ]]; then
    echo "  ✓ $name (already linked)"
  elif [[ -f "$target" ]]; then
    echo "  ⚠️ $name exists (not a symlink) — skipping. Remove it manually to use the repo version."
  else
    ln -s "$f" "$target"
    echo "  ✓ $name"
  fi
done

# --- Task scripts ---

echo ""
echo "Installing task scripts → $REPOS_ROOT"
for f in "$REPO_DIR"/scripts/{new-task,add-repo,done-task,cleanup-merged-tasks}.sh; do
  [[ -f "$f" ]] || continue
  name=$(basename "$f")
  target="$REPOS_ROOT/$name"
  if [[ -L "$target" ]]; then
    echo "  ✓ $name (already linked)"
  elif [[ -f "$target" ]]; then
    echo "  ⚠️ $name exists (not a symlink) — skipping."
  else
    ln -s "$f" "$target"
    echo "  ✓ $name"
  fi
done

# --- Workspace git settings ---
# Prevent main workspace from discovering worktree repos in the SCM view

echo ""
echo "Patching workspace git settings"
for ws in "$REPOS_ROOT"/*.code-workspace; do
  [[ -f "$ws" ]] || continue
  name=$(basename "$ws")
  if grep -q '"git.autoRepositoryDetection"' "$ws" 2>/dev/null; then
    echo "  ✓ $name (already patched)"
  elif command -v python3 &>/dev/null; then
    python3 -c "
import json, sys
with open(sys.argv[1], 'r') as f:
    ws = json.load(f)
s = ws.setdefault('settings', {})
s['git.autoRepositoryDetection'] = False
# Scope scanning to folders defined in the workspace
repos = []
for folder in ws.get('folders', []):
    p = folder.get('path', '')
    if '/' not in p:
        repos.append(p)
if repos:
    s['git.scanRepositories'] = repos
with open(sys.argv[1], 'w') as f:
    json.dump(ws, f, indent=2)
    f.write('\n')
" "$ws" && echo "  ✓ $name (patched)" || echo "  ⚠️ $name — failed to patch"
  else
    echo "  ⚠️ $name — python3 not found, skipping"
  fi
done

# --- Cleanup scheduler (launchd) ---

if [[ "$(uname)" == "Darwin" ]]; then
  PLIST_NAME="com.copilot-prompts.cleanup-merged-tasks"
  PLIST_SRC="$REPO_DIR/scripts/${PLIST_NAME}.plist"
  PLIST_TARGET="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
  CLEANUP_SCRIPT="$REPOS_ROOT/cleanup-merged-tasks.sh"

  echo ""
  echo "Installing cleanup scheduler → $PLIST_TARGET"

  if [[ -f "$PLIST_SRC" && -L "$CLEANUP_SCRIPT" || -x "$CLEANUP_SCRIPT" ]]; then
    # Patch the plist with the actual script path
    sed "s|CLEANUP_SCRIPT_PATH|${CLEANUP_SCRIPT}|g" "$PLIST_SRC" > "$PLIST_TARGET"

    # Load the agent (unload first if already loaded)
    launchctl unload "$PLIST_TARGET" 2>/dev/null
    launchctl load "$PLIST_TARGET"
    echo "  ✓ Launchd agent loaded (runs weekdays 9am-7pm every 2h)"
  else
    echo "  ⚠️ cleanup-merged-tasks.sh not found — skipping scheduler"
  fi
fi

echo ""
echo "✅ Done. Pull this repo and re-run to update."
