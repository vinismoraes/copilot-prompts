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
PROFILE="core"
PRUNE=false
CONFIGURE_SHELL_PATH=true

usage() {
  echo "Usage: $0 [--profile core|league|all] [--prune] [--no-shell-path]"
  echo ""
  echo "Profiles:"
  echo "  core   Generic prompts/instructions (default)"
  echo "  league Core + League-specific prompts/instructions"
  echo "  all    Install everything in instructions/ and prompts/"
  echo ""
  echo "Options:"
  echo "  --prune  Remove repo-managed symlinks not selected by profile"
  echo "  --no-shell-path  Do not update shell rc file to include REPOS_ROOT in PATH"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --prune)
      PRUNE=true
      shift
      ;;
    --no-shell-path)
      CONFIGURE_SHELL_PATH=false
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ "$PROFILE" != "core" && "$PROFILE" != "league" && "$PROFILE" != "all" ]]; then
  echo "Invalid profile: $PROFILE"
  usage
  exit 1
fi

typeset -a instruction_files
typeset -a prompt_files

core_instructions=(
  "core/diagrams.instructions.md"
  "core/git-commits.instructions.md"
  "core/git-push.instructions.md"
  "core/go-standards.instructions.md"
  "core/pre-commit-lint.instructions.md"
  "core/pr-creation.instructions.md"
  "core/pr-reviews.instructions.md"
  "core/task-workflow.instructions.md"
)

league_instructions=(
  "league/circleci.instructions.md"
  "league/league-security-policy.instructions.md"
  "league/locale-ignore.instructions.md"
  "league/mcp-tools.instructions.md"
  "league/mirrord.instructions.md"
  "league/pr-creation.instructions.md"
  "league/pr-reviews.instructions.md"
)

core_prompts=(
  "core/quick-start-repo.prompt.md"
)

league_prompts=(
  "league/mirrord.prompt.md"
)

if [[ "$PROFILE" == "all" ]]; then
  while IFS= read -r f; do
    instruction_files+=("${f#$REPO_DIR/instructions/}")
  done < <(find "$REPO_DIR/instructions" -type f -name "*.instructions.md" | sort)
  while IFS= read -r f; do
    prompt_files+=("${f#$REPO_DIR/prompts/}")
  done < <(find "$REPO_DIR/prompts" -type f -name "*.prompt.md" | sort)
elif [[ "$PROFILE" == "league" ]]; then
  instruction_files=("${core_instructions[@]}" "${league_instructions[@]}")
  prompt_files=("${core_prompts[@]}" "${league_prompts[@]}")
else
  instruction_files=("${core_instructions[@]}")
  prompt_files=("${core_prompts[@]}")
fi

typeset -a selected_names
for relpath in "${instruction_files[@]}" "${prompt_files[@]}"; do
  selected_names+=("$(basename "$relpath")")
done

is_selected_name() {
  local candidate="$1"
  local item
  for item in "${selected_names[@]}"; do
    if [[ "$item" == "$candidate" ]]; then
      return 0
    fi
  done
  return 1
}

link_file() {
  local source_file="$1"
  local target_file="$2"
  local name
  name=$(basename "$source_file")
  if [[ -L "$target_file" ]]; then
    local current
    current=$(readlink "$target_file")
    if [[ "$current" == "$source_file" ]]; then
      echo "  ✓ $name (already linked)"
    else
      ln -sf "$source_file" "$target_file"
      echo "  ✓ $name (updated link)"
    fi
  elif [[ -f "$target_file" ]]; then
    echo "  ⚠️ $name exists (not a symlink) — skipping. Remove it manually to use the repo version."
  else
    ln -s "$source_file" "$target_file"
    echo "  ✓ $name"
  fi
}

prune_unselected() {
  local directory="$1"
  for target in "$directory"/*.instructions.md "$directory"/*.prompt.md; do
    [[ -L "$target" ]] || continue
    local resolved
    resolved=$(readlink "$target")
    [[ "$resolved" == "$REPO_DIR"/* ]] || continue
    local name
    name=$(basename "$target")
    if ! is_selected_name "$name"; then
      rm "$target"
      echo "  - pruned $name"
    fi
  done
}

# --- Prompts ---

case "$(uname)" in
  Darwin) PROMPTS_DIR="$HOME/Library/Application Support/Code/User/prompts" ;;
  Linux)  PROMPTS_DIR="$HOME/.config/Code/User/prompts" ;;
  *)      echo "Unsupported OS"; exit 1 ;;
esac

mkdir -p "$PROMPTS_DIR"

echo "Installing prompts/profile=$PROFILE → $PROMPTS_DIR"
for relpath in "${instruction_files[@]}"; do
  source="$REPO_DIR/instructions/$relpath"
  name=$(basename "$relpath")
  target="$PROMPTS_DIR/$name"
  if [[ -f "$source" ]]; then
    link_file "$source" "$target"
  else
    echo "  ⚠️ Missing instruction: $relpath"
  fi
done

for relpath in "${prompt_files[@]}"; do
  source="$REPO_DIR/prompts/$relpath"
  name=$(basename "$relpath")
  target="$PROMPTS_DIR/$name"
  if [[ -f "$source" ]]; then
    link_file "$source" "$target"
  else
    echo "  ⚠️ Missing prompt: $relpath"
  fi
done

if [[ "$PRUNE" == true ]]; then
  echo "Pruning repo-managed links not in profile..."
  prune_unselected "$PROMPTS_DIR"
fi

# --- Task scripts ---

echo ""
echo "Installing task scripts → $REPOS_ROOT"
for f in "$REPO_DIR"/scripts/{new-task,add-repo,done-task,quick-start-repo}.sh; do
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

# Make task commands executable from shell without typing full paths.
echo ""
echo "Validating task command availability..."

if [[ "$CONFIGURE_SHELL_PATH" == true && ":$PATH:" != *":$REPOS_ROOT:"* ]]; then
  export PATH="$REPOS_ROOT:$PATH"
fi

shell_name=$(basename "$SHELL")
rc_file=""
if [[ "$shell_name" == "zsh" ]]; then
  rc_file="$HOME/.zshrc"
elif [[ "$shell_name" == "bash" ]]; then
  rc_file="$HOME/.bashrc"
fi

if [[ "$CONFIGURE_SHELL_PATH" == true && -n "$rc_file" ]]; then
  mkdir -p "$(dirname "$rc_file")"
  touch "$rc_file"
  path_line="export PATH=\"$REPOS_ROOT:\$PATH\""
  if ! grep -F "$path_line" "$rc_file" >/dev/null 2>&1; then
    {
      echo ""
      echo "# Added by copilot-prompts installer"
      echo "$path_line"
    } >> "$rc_file"
    echo "  ✓ Added $REPOS_ROOT to PATH in $rc_file"
  fi
fi

for cmd in new-task.sh add-repo.sh done-task.sh quick-start-repo.sh; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ✓ $cmd is callable"
  else
    echo "  ⚠️ $cmd not found in PATH (open a new shell or add $REPOS_ROOT to PATH)"
  fi
done

echo ""
echo "✅ Done. Pull this repo and re-run to update."
