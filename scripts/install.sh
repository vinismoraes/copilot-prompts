#!/bin/zsh
# Installs copilot prompts and task scripts.
#
# Prompts:  symlinked into VS Code's user prompts directory
# Scripts:  symlinked into $REPOS_ROOT (default: ~/GoProjects)
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
for f in "$REPO_DIR"/scripts/{new-task,add-repo,done-task}.sh; do
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

echo ""
echo "✅ Done. Pull this repo and re-run to update."
