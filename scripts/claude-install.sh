#!/bin/zsh
# Installs prompts into Claude Code's user config directory.
#
# Sister script to install.sh (which targets VS Code Copilot). Same profile UX,
# same symlink pattern. Instruction files land in ~/.claude/instructions/, slash
# commands in ~/.claude/commands/ (with the .prompt suffix stripped so /name works).
#
# It also regenerates the "AUTO-INSTALLED INSTRUCTIONS" block inside
# ~/.claude/CLAUDE.md so Claude actually loads the imports on session start.
# Content outside the markers is preserved.
#
# Re-running is safe — existing symlinks are updated, non-symlink files are skipped
# unless --force is passed.
#
# Usage:
#   ./claude-install.sh                                # core profile (default)
#   ./claude-install.sh --profile <pack>               # core + <pack>
#   ./claude-install.sh --profile league,personal      # core + league + personal (comma-sep)
#   ./claude-install.sh --profile league --profile personal  # or repeat the flag
#   ./claude-install.sh --profile all                  # every pack
#   ./claude-install.sh --profile core --prune         # remove links not in selected profile
#   ./claude-install.sh --force                        # overwrite regular files with symlinks

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

typeset -a REQUESTED_PROFILES
REQUESTED_PROFILES=()
PRUNE=false
FORCE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      # Accept both repeated flags (--profile a --profile b) and comma-separated (--profile a,b)
      for p in ${(s:,:)2}; do
        REQUESTED_PROFILES+=("$p")
      done
      shift 2 ;;
    --prune) PRUNE=true; shift ;;
    --force) FORCE=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Default profile is core
[[ ${#REQUESTED_PROFILES[@]} -eq 0 ]] && REQUESTED_PROFILES=("core")

# Auto-discover available packs
typeset -a AVAILABLE_PACKS
AVAILABLE_PACKS=("core")
for d in "$REPO_DIR"/instructions/*/(N) "$REPO_DIR"/prompts/*/(N); do
  pack=$(basename "$d")
  if [[ ! " ${AVAILABLE_PACKS[*]} " =~ " $pack " ]]; then
    AVAILABLE_PACKS+=("$pack")
  fi
done

# Validate each requested profile
for p in "${REQUESTED_PROFILES[@]}"; do
  if [[ "$p" != "all" && ! " ${AVAILABLE_PACKS[*]} " =~ " $p " ]]; then
    echo "Unknown profile: $p"
    echo "Available: ${AVAILABLE_PACKS[*]} all"
    exit 1
  fi
done

# Build the deduped list of dirs to install
typeset -a PROFILE_DIRS
PROFILE_DIRS=("core")
for p in "${REQUESTED_PROFILES[@]}"; do
  if [[ "$p" == "all" ]]; then
    PROFILE_DIRS=("${AVAILABLE_PACKS[@]}")
    break
  fi
  if [[ ! " ${PROFILE_DIRS[*]} " =~ " $p " ]]; then
    PROFILE_DIRS+=("$p")
  fi
done

CLAUDE_DIR="$HOME/.claude"
INSTRUCTIONS_DIR="$CLAUDE_DIR/instructions"
COMMANDS_DIR="$CLAUDE_DIR/commands"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

mkdir -p "$INSTRUCTIONS_DIR" "$COMMANDS_DIR"

# Track installed filenames per dir so we can prune and regenerate CLAUDE.md
typeset -a INSTALLED_INSTRUCTIONS
typeset -a INSTALLED_COMMANDS

link_file() {
  local src="$1" target="$2" name="$3" bucket="$4"
  case "$bucket" in
    instructions) INSTALLED_INSTRUCTIONS+=("$name") ;;
    commands)     INSTALLED_COMMANDS+=("$name") ;;
  esac
  if [[ -L "$target" ]]; then
    local current
    current=$(readlink "$target")
    if [[ "$current" == "$src" ]]; then
      echo "  ✓ $name (up to date)"
    else
      ln -sf "$src" "$target"
      echo "  ✓ $name (updated)"
    fi
  elif [[ -f "$target" ]]; then
    if $FORCE; then
      rm "$target"
      ln -s "$src" "$target"
      echo "  ↻ $name (replaced regular file with symlink)"
    else
      echo "  ⚠  $name exists (not a symlink) — skipping. Re-run with --force to replace."
    fi
  else
    ln -s "$src" "$target"
    echo "  + $name"
  fi
}

echo "Installing Claude Code config (profiles: ${PROFILE_DIRS[*]}) → $CLAUDE_DIR"
echo ""

for pack in "${PROFILE_DIRS[@]}"; do
  # Instructions keep their filename (~/.claude/instructions/*.instructions.md)
  for f in "$REPO_DIR"/instructions/"$pack"/*.instructions.md(N); do
    link_file "$f" "$INSTRUCTIONS_DIR/$(basename "$f")" "$(basename "$f")" instructions
  done
  # Prompts become slash commands: foo.prompt.md → ~/.claude/commands/foo.md
  for f in "$REPO_DIR"/prompts/"$pack"/*.prompt.md(N); do
    base=$(basename "$f" .prompt.md)
    link_file "$f" "$COMMANDS_DIR/${base}.md" "${base}.md (/$base)" commands
  done
done

# --- Prune ---
if $PRUNE; then
  echo ""
  echo "Pruning stale links..."
  for target in "$INSTRUCTIONS_DIR"/*.instructions.md(N); do
    [[ -L "$target" ]] || continue
    link_dest=$(readlink "$target")
    [[ "$link_dest" == "$REPO_DIR"/* ]] || continue
    name=$(basename "$target")
    if [[ ! " ${INSTALLED_INSTRUCTIONS[*]} " =~ " $name " ]]; then
      rm "$target"
      echo "  - instructions/$name (removed)"
    fi
  done
  for target in "$COMMANDS_DIR"/*.md(N); do
    [[ -L "$target" ]] || continue
    link_dest=$(readlink "$target")
    [[ "$link_dest" == "$REPO_DIR"/* ]] || continue
    name=$(basename "$target")
    label="$name (/$(basename "$name" .md))"
    if [[ ! " ${INSTALLED_COMMANDS[*]} " =~ " $label " ]]; then
      rm "$target"
      echo "  - commands/$name (removed)"
    fi
  done
fi

# --- Regenerate the AUTO-INSTALLED INSTRUCTIONS block in CLAUDE.md ---
if [[ -f "$CLAUDE_MD" ]]; then
  BEGIN="<!-- BEGIN AUTO-INSTALLED INSTRUCTIONS"
  END="<!-- END AUTO-INSTALLED INSTRUCTIONS -->"

  if grep -qF "$BEGIN" "$CLAUDE_MD" && grep -qF "$END" "$CLAUDE_MD"; then
    tmp=$(mktemp)
    awk -v begin="$BEGIN" -v end="$END" '
      $0 ~ begin { print; skip=1; system("cat /tmp/.claude-imports.$$"); next }
      $0 ~ end   { skip=0; print; next }
      !skip
    ' > /tmp/.claude-imports-wrapped.$$ < "$CLAUDE_MD" 2>/dev/null || true

    # Build the imports list (sorted for stability)
    {
      for name in "${INSTALLED_INSTRUCTIONS[@]}"; do
        echo "@instructions/$name"
      done | sort -u
    } > /tmp/.claude-imports.$$

    awk -v begin="$BEGIN" -v end="$END" -v imports="/tmp/.claude-imports.$$" '
      BEGIN { skip=0 }
      {
        if ($0 ~ begin) {
          print
          while ((getline line < imports) > 0) print line
          close(imports)
          skip=1
          next
        }
        if ($0 ~ end) { skip=0; print; next }
        if (!skip) print
      }
    ' "$CLAUDE_MD" > "$tmp"
    mv "$tmp" "$CLAUDE_MD"
    unique_count=$(sort -u /tmp/.claude-imports.$$ | wc -l | tr -d ' ')
    rm -f /tmp/.claude-imports.$$ /tmp/.claude-imports-wrapped.$$
    echo ""
    echo "  ✓ CLAUDE.md instructions block regenerated ($unique_count imports)"
  else
    echo ""
    echo "  ⚠  CLAUDE.md exists but has no AUTO-INSTALLED INSTRUCTIONS markers — skipping regeneration."
    echo "     Add these lines around your @instructions/* imports to enable auto-management:"
    echo "       <!-- BEGIN AUTO-INSTALLED INSTRUCTIONS -->"
    echo "       @instructions/..."
    echo "       <!-- END AUTO-INSTALLED INSTRUCTIONS -->"
  fi
else
  echo ""
  echo "  ⚠  $CLAUDE_MD not found — instructions won't be loaded until you create it with @instructions/* imports."
fi

echo ""
echo "✅ Done. Pull this repo and re-run to update."
