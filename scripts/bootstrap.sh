#!/bin/zsh
# Bootstrap a new machine with the full dev environment.
#
# Prerequisites:
#   - macOS with Homebrew installed
#   - GitHub CLI authenticated (gh auth login)
#   - This repo cloned to ~/GoProjects/copilot-prompts
#
# Usage:
#   ./scripts/bootstrap.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Installing Brew packages ==="
brew install lazygit atuin direnv
brew install --cask raycast ghostty obsidian

echo ""
echo "=== Configuring shell ==="

ZSHRC="$HOME/.zshrc"

append_if_missing() {
  local marker="$1" line="$2"
  if ! grep -qF "$marker" "$ZSHRC" 2>/dev/null; then
    echo "" >> "$ZSHRC"
    echo "$line" >> "$ZSHRC"
    echo "  + added: $marker"
  else
    echo "  ✓ already present: $marker"
  fi
}

append_if_missing 'alias lg=' '# Lazygit
alias lg="lazygit"'

append_if_missing 'atuin init' '# Atuin shell history
eval "$(atuin init zsh --disable-up-arrow)"'

append_if_missing 'direnv hook' '# direnv
eval "$(direnv hook zsh)"'

append_if_missing 'OBSIDIAN_API_KEY' '# Obsidian Local REST API — replace with your key after enabling the plugin
export OBSIDIAN_API_KEY="REPLACE_ME"'

echo ""
echo "=== Configuring tools ==="

# Atuin — local only, no cloud sync
mkdir -p ~/.config/atuin
cat > ~/.config/atuin/config.toml << 'ATUIN'
sync_address = ""
sync.records = false
search_mode = "fuzzy"
filter_mode = "global"
style = "compact"
show_preview = true
show_help = true
secrets_filter = true
ATUIN
echo "  ✓ ~/.config/atuin/config.toml"

# Ghostty
mkdir -p ~/.config/ghostty
cat > ~/.config/ghostty/config << 'GHOSTTY'
font-family = Menlo
font-size = 14
theme = Catppuccin Mocha
window-padding-x = 8
window-padding-y = 4
window-decoration = true
macos-titlebar-style = tabs
copy-on-select = clipboard
confirm-close-surface = false
shell-integration = zsh
auto-update = check
GHOSTTY
echo "  ✓ ~/.config/ghostty/config"

# direnv — hide env diff noise
mkdir -p ~/.config/direnv
cat > ~/.config/direnv/direnv.toml << 'DIRENV'
[global]
hide_env_diff = true
DIRENV
echo "  ✓ ~/.config/direnv/direnv.toml"

echo ""
echo "=== Configuring VS Code MCP ==="

case "$(uname)" in
  Darwin) MCP_DIR="$HOME/Library/Application Support/Code/User" ;;
  Linux)  MCP_DIR="$HOME/.config/Code/User" ;;
esac

mkdir -p "$MCP_DIR"
if [[ ! -f "$MCP_DIR/mcp.json" ]] || [[ ! -s "$MCP_DIR/mcp.json" ]]; then
  cat > "$MCP_DIR/mcp.json" << 'MCP'
{
    "servers": {
        "obsidian": {
            "command": "uvx",
            "args": ["mcp-obsidian"],
            "env": {
                "OBSIDIAN_API_KEY": "${env:OBSIDIAN_API_KEY}"
            }
        }
    }
}
MCP
  echo "  ✓ mcp.json created"
else
  echo "  ✓ mcp.json already exists — skipping"
fi

echo ""
echo "=== Cloning Obsidian vault ==="

if [[ -d "$HOME/ObsidianVault/.git" ]]; then
  echo "  ✓ ~/ObsidianVault already exists"
  cd "$HOME/ObsidianVault" && git pull
else
  gh repo clone vinismoraes/obsidian-vault "$HOME/ObsidianVault"
  echo "  ✓ cloned to ~/ObsidianVault"
fi

echo ""
echo "=== Installing Copilot prompts ==="

"$REPO_DIR/scripts/install.sh" --profile league

echo ""
echo "=== Done ==="
echo ""
echo "Next steps:"
echo "  1. Open Obsidian → Open folder as vault → ~/ObsidianVault"
echo "  2. Enable community plugins: Calendar, Templater, Dataview, Local REST API"
echo "  3. Copy the REST API key from plugin settings into OBSIDIAN_API_KEY in ~/.zshrc"
echo "  4. Restart your terminal or run: source ~/.zshrc"
echo "  5. Open Raycast and complete initial setup"
