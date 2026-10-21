#!/bin/sh
# Optional macOS tool setup. Repeated runs preserve the installed package.
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ "$(uname -s)" != Darwin ]; then
  echo "Awake currently supports macOS only; prompts can be installed without --awake." >&2
  exit 1
fi
exec python3 "$SCRIPT_DIR/awake/install.py" --ensure "$@"
