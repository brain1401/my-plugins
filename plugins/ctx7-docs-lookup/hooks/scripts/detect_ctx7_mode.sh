#!/usr/bin/env bash
# Detect context7 MCP availability and set CTX7_MODE environment variable.
# Runs as a SessionStart hook. Always exits 0 to never block session start.

# Guarantee exit 0 on any unexpected error
trap 'exit 0' ERR

set -uo pipefail

# Guard: if CLAUDE_ENV_FILE is not set, skip detection
if [[ -z "${CLAUDE_ENV_FILE:-}" ]]; then
  exit 0
fi

# Guard: if CTX7_MODE is already set, skip (idempotency)
if grep -q "^export CTX7_MODE=" "$CLAUDE_ENV_FILE" 2>/dev/null; then
  exit 0
fi

# Guard: if jq is not installed, set unknown mode
if ! command -v jq &>/dev/null; then
  echo "export CTX7_MODE=unknown" >> "$CLAUDE_ENV_FILE"
  exit 0
fi

# Config files to check (priority order)
CONFIG_FILES=(
  "${CLAUDE_PROJECT_DIR:-.}/.mcp.json"
  "${CLAUDE_PROJECT_DIR:-.}/.claude/settings.json"
  "${CLAUDE_PROJECT_DIR:-.}/.claude/settings.local.json"
  "${HOME}/.claude/.mcp.json"
  "${HOME}/.claude/settings.json"
  "${HOME}/.claude/settings.local.json"
)

# Check each config file for context7 MCP server
for config in "${CONFIG_FILES[@]}"; do
  if [[ ! -f "$config" ]]; then
    continue
  fi

  # Extract mcpServers keys and check for context7/ctx7 (case-insensitive)
  # Use 2>/dev/null to handle malformed JSON gracefully
  if jq -e '(.mcpServers // {}) | keys[] | test("context7|ctx7"; "i")' "$config" 2>/dev/null | grep -q true; then
    echo "export CTX7_MODE=mcp" >> "$CLAUDE_ENV_FILE"
    exit 0
  fi
done

# No MCP config found — fall back to skill mode
echo "export CTX7_MODE=skill" >> "$CLAUDE_ENV_FILE"
exit 0
