#!/bin/zsh
# Bootstrap a new bare repo under REPOS_ROOT with an initial main commit.
# After running this, use new-task.sh to create a worktree/branch for your task.
#
# Usage:
#   ./quick-start-repo.sh REPO_NAME [--lang go|node|python|blank] [--module MODULE_PATH]
#
# Options:
#   --lang     Language preset for .gitignore and scaffolding (default: go)
#   --module   Go module path — only used when --lang go (default: github.com/USER/REPO_NAME)
#
# Examples:
#   ./quick-start-repo.sh my-api
#   ./quick-start-repo.sh my-api --module github.com/acme/my-api
#   ./quick-start-repo.sh infiltrator --lang node
#   ./quick-start-repo.sh data-pipeline --lang python
#   ./quick-start-repo.sh notes --lang blank

set -e

REPOS_ROOT=${REPOS_ROOT:-~/GoProjects}

REPO_NAME="$1"
if [[ -z "$REPO_NAME" || "$REPO_NAME" == "--help" || "$REPO_NAME" == "-h" ]]; then
  echo "Usage: $0 REPO_NAME [--lang go|node|python|blank] [--module MODULE_PATH]"
  echo ""
  echo "Options:"
  echo "  --lang     go (default), node, python, blank"
  echo "  --module   Go module path (only for --lang go)"
  echo ""
  echo "Examples:"
  echo "  $0 my-api"
  echo "  $0 infiltrator --lang node"
  echo "  $0 data-pipeline --lang python"
  exit 0
fi
shift

LANG="go"
MODULE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang)   LANG="$2";   shift 2 ;;
    --module) MODULE="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

case "$LANG" in
  go|node|python|blank) ;;
  *) echo "Unknown --lang: $LANG (expected: go, node, python, blank)"; exit 1 ;;
esac

REPO_PATH="$REPOS_ROOT/$REPO_NAME"

if [[ -d "$REPO_PATH" ]]; then
  echo "❌ Directory already exists: $REPO_PATH"
  exit 1
fi

echo "→ Creating repo at $REPO_PATH (lang: $LANG)..."
mkdir -p "$REPO_PATH"
cd "$REPO_PATH"

git init -b main

# ── .gitignore ──────────────────────────────────────────────────────────────

case "$LANG" in
  go)
    cat > .gitignore <<'EOF'
# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib
/bin/

# Test / coverage
*.test
*.out
coverage.txt

# Go workspace
go.work
go.work.sum

# Env
.env
.env.*
EOF
    ;;
  node)
    cat > .gitignore <<'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Build output
.next/
out/
dist/
build/

# Env
.env
.env.*
!.env.example

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Misc
.DS_Store
*.pem
.vercel
EOF
    ;;
  python)
    cat > .gitignore <<'EOF'
# Virtual envs
.venv/
venv/
env/

# Byte-compiled
__pycache__/
*.py[cod]
*$py.class
*.pyo

# Distribution
dist/
build/
*.egg-info/

# Env
.env
.env.*

# Testing
.pytest_cache/
.coverage
htmlcov/

# Misc
.DS_Store
EOF
    ;;
  blank)
    cat > .gitignore <<'EOF'
.DS_Store
.env
.env.*
EOF
    ;;
esac

# ── Language scaffolding ─────────────────────────────────────────────────────

case "$LANG" in
  go)
    if [[ -z "$MODULE" ]]; then
      GH_USER=$(git config --global github.user 2>/dev/null || echo "user")
      MODULE="github.com/${GH_USER}/${REPO_NAME}"
    fi
    echo "→ Initialising Go module: $MODULE"
    go mod init "$MODULE"
    ;;
  node)
    cat > package.json <<EOF
{
  "name": "${REPO_NAME}",
  "version": "0.1.0",
  "private": true
}
EOF
    ;;
  python)
    cat > pyproject.toml <<EOF
[project]
name = "${REPO_NAME}"
version = "0.1.0"
EOF
    ;;
  blank)
    # nothing extra
    ;;
esac

# ── README ───────────────────────────────────────────────────────────────────

cat > README.md <<EOF
# ${REPO_NAME}
EOF

# ── Initial commit ───────────────────────────────────────────────────────────

git add -A
git commit -m "initial commit"

echo ""
echo "✅ Repo ready: $REPO_PATH"
echo "   Branch: main"
echo ""
echo "   Next step:"
echo "   ~/GoProjects/new-task.sh YOUR_BRANCH ${REPO_NAME}"
