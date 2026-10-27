#!/bin/zsh
# Installs copilot prompts into VS Code's user prompts directory.
#
# Re-running is safe — existing symlinks are updated, non-symlink files are skipped.
#
# Usage:
#   ./install.sh                        # core profile (default)
#   ./install.sh --profile <pack>       # core + <pack> (any folder under instructions/ or prompts/)
#   ./install.sh --profile all          # every pack
#   ./install.sh --profile core --prune # remove links not in selected profile
#   ./install.sh --codex-efficiency    # generic Codex kit in ~/.codex

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

PROFILE="core"
PRUNE=false
AWAKE=false
AWAKE_CODEX=false
CODEX_EFFICIENCY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --prune) PRUNE=true; shift ;;
    --awake) AWAKE=true; shift ;;
    --awake-codex) AWAKE=true; AWAKE_CODEX=true; shift ;;
    --codex-efficiency) CODEX_EFFICIENCY=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Auto-discover available packs from filesystem
typeset -a AVAILABLE_PACKS
AVAILABLE_PACKS=("core")
for d in "$REPO_DIR"/instructions/*/(N) "$REPO_DIR"/prompts/*/(N); do
  pack=$(basename "$d")
  if [[ ! " ${AVAILABLE_PACKS[*]} " =~ " $pack " ]]; then
    AVAILABLE_PACKS+=("$pack")
  fi
done

# Validate profile
if [[ "$PROFILE" != "all" && ! " ${AVAILABLE_PACKS[*]} " =~ " $PROFILE " ]]; then
  echo "Unknown profile: $PROFILE"
  echo "Available: ${AVAILABLE_PACKS[*]} all"
  exit 1
fi

# Build list of profile directories to install
typeset -a PROFILE_DIRS
if [[ "$PROFILE" == "all" ]]; then
  PROFILE_DIRS=("${AVAILABLE_PACKS[@]}")
elif [[ "$PROFILE" == "core" ]]; then
  PROFILE_DIRS=("core")
else
  PROFILE_DIRS=("core" "$PROFILE")
fi

if $CODEX_EFFICIENCY; then
  if [[ " ${PROFILE_DIRS[*]} " =~ " league " ]]; then
    echo "Install organization prompts separately; use report-only for an existing organizational Codex profile."
    exit 1
  fi
  python3 "$SCRIPT_DIR/codex-efficiency/install.py" --check
fi

# --- Prompts ---

if $AWAKE; then
  if [[ ! " ${PROFILE_DIRS[*]} " =~ " awake " ]]; then
    PROFILE_DIRS+=("awake")
  fi
  if $AWAKE_CODEX; then
    "$SCRIPT_DIR/install-awake.sh" --codex
  else
    "$SCRIPT_DIR/install-awake.sh"
  fi
fi

case "$(uname)" in
  Darwin) PROMPTS_DIR="$HOME/Library/Application Support/Code/User/prompts" ;;
  Linux)  PROMPTS_DIR="$HOME/.config/Code/User/prompts" ;;
  *)      echo "Unsupported OS"; exit 1 ;;
esac

mkdir -p "$PROMPTS_DIR"

# Track which files we install (for pruning)
typeset -a INSTALLED_NAMES

link_file() {
  local src="$1" target="$2" name="$3"
  INSTALLED_NAMES+=("$name")
  if [[ -L "$target" ]]; then
    # Update existing symlink to point to current source
    local current
    current=$(readlink "$target")
    if [[ "$current" == "$src" ]]; then
      echo "  ✓ $name (up to date)"
    else
      ln -sf "$src" "$target"
      echo "  ✓ $name (updated)"
    fi
  elif [[ -f "$target" ]]; then
    echo "  ⚠  $name exists (not a symlink) — skipping. Remove it manually to use the repo version."
  else
    ln -s "$src" "$target"
    echo "  + $name"
  fi
}

echo "Installing prompts (profile: $PROFILE) → $PROMPTS_DIR"
echo ""

for pack in "${PROFILE_DIRS[@]}"; do
  # Instructions
  for f in "$REPO_DIR"/instructions/"$pack"/*.instructions.md(N); do
    link_file "$f" "$PROMPTS_DIR/$(basename "$f")" "$(basename "$f")"
  done
  # Prompts
  for f in "$REPO_DIR"/prompts/"$pack"/*.prompt.md(N); do
    link_file "$f" "$PROMPTS_DIR/$(basename "$f")" "$(basename "$f")"
  done
done

# --- Prune stale links ---

if $PRUNE; then
  echo ""
  echo "Pruning stale links..."
  for target in "$PROMPTS_DIR"/*.instructions.md "$PROMPTS_DIR"/*.prompt.md; do
    [[ -L "$target" ]] || continue
    # Only prune symlinks that point into our repo
    local link_dest
    link_dest=$(readlink "$target")
    [[ "$link_dest" == "$REPO_DIR"/* ]] || continue
    name=$(basename "$target")
    if [[ ! " ${INSTALLED_NAMES[*]} " =~ " $name " ]]; then
      rm "$target"
      echo "  - $name (removed)"
    fi
  done
fi

echo ""
if $CODEX_EFFICIENCY; then
  echo ""
  echo "Installing Codex efficiency tools..."
  python3 "$SCRIPT_DIR/codex-efficiency/install.py" --apply
fi

echo "✅ Done. Pull this repo and re-run to update."
