# ctx7-docs-lookup Dual Mode Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ctx7-docs-lookup 플러그인이 MCP와 CLI(skill) 두 방식을 자동 감지하고 적절한 경로로 안내하도록 업데이트

**Architecture:** SessionStart hook이 `jq`로 MCP 설정 파일을 파싱하여 `CTX7_MODE` 환경 변수를 세션에 저장. SKILL.md와 rules.md가 이 환경 변수에 따라 조건 분기.

**Tech Stack:** Bash, jq, Claude Code plugin hooks, Markdown

**Spec:** `docs/superpowers/specs/2026-03-24-ctx7-dual-mode-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh` | **Create** | SessionStart 시 MCP 설정 감지 → `$CLAUDE_ENV_FILE`에 `CTX7_MODE` 기록 |
| `plugins/ctx7-docs-lookup/hooks/hooks.json` | **Edit** | SessionStart hook 등록 |
| `plugins/ctx7-docs-lookup/hooks/rules.md` | **Edit** | 모드 중립적 표현으로 변경 |
| `plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md` | **Edit** | "How to Use context7" 섹션을 `$CTX7_MODE` 조건 분기로 교체 |

---

### Task 1: Create detect_ctx7_mode.sh

**Files:**
- Create: `plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh`

- [ ] **Step 1: Create the detection script**

```bash
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
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh`

- [ ] **Step 3: Test with a mock .mcp.json containing context7**

Run:
```bash
# Create temp test environment
TEST_DIR=$(mktemp -d)
cat > "$TEST_DIR/.mcp.json" << 'TESTEOF'
{"mcpServers":{"context7":{"command":"npx","args":["-y","@anthropic/context7-mcp"]}}}
TESTEOF
CLAUDE_ENV_FILE="$TEST_DIR/env" CLAUDE_PROJECT_DIR="$TEST_DIR" \
  bash plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh
cat "$TEST_DIR/env"
rm -rf "$TEST_DIR"
```

Expected output: `export CTX7_MODE=mcp`

- [ ] **Step 4: Test with no MCP config (skill fallback)**

Run:
```bash
TEST_DIR=$(mktemp -d)
CLAUDE_ENV_FILE="$TEST_DIR/env" CLAUDE_PROJECT_DIR="$TEST_DIR" \
  bash plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh
cat "$TEST_DIR/env"
rm -rf "$TEST_DIR"
```

Expected output: `export CTX7_MODE=skill`

- [ ] **Step 5: Test with variant key name (ctx7-server)**

Run:
```bash
TEST_DIR=$(mktemp -d)
cat > "$TEST_DIR/.mcp.json" << 'TESTEOF'
{"mcpServers":{"my-ctx7-server":{"command":"npx","args":["ctx7"]}}}
TESTEOF
CLAUDE_ENV_FILE="$TEST_DIR/env" CLAUDE_PROJECT_DIR="$TEST_DIR" \
  bash plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh
cat "$TEST_DIR/env"
rm -rf "$TEST_DIR"
```

Expected output: `export CTX7_MODE=mcp`

- [ ] **Step 6: Test with malformed JSON (unknown fallback)**

Run:

```bash
TEST_DIR=$(mktemp -d)
echo "NOT VALID JSON{{{" > "$TEST_DIR/.mcp.json"
CLAUDE_ENV_FILE="$TEST_DIR/env" CLAUDE_PROJECT_DIR="$TEST_DIR" \
  bash plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh
cat "$TEST_DIR/env"
rm -rf "$TEST_DIR"
```

Expected output: `export CTX7_MODE=skill` (malformed JSON is silently skipped, no MCP found → skill mode)

- [ ] **Step 7: Commit**

```bash
git add plugins/ctx7-docs-lookup/hooks/scripts/detect_ctx7_mode.sh
git commit -m "feat: add SessionStart detection script for ctx7 mode"
```

---

### Task 2: Update hooks.json

**Files:**
- Modify: `plugins/ctx7-docs-lookup/hooks/hooks.json`

- [ ] **Step 1: Add SessionStart hook to hooks.json**

Replace the entire file content with:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/detect_ctx7_mode.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/detect_repeated_errors.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `jq . plugins/ctx7-docs-lookup/hooks/hooks.json`
Expected: Valid JSON output with no errors

- [ ] **Step 3: Commit**

```bash
git add plugins/ctx7-docs-lookup/hooks/hooks.json
git commit -m "feat: register SessionStart hook for ctx7 mode detection"
```

---

### Task 3: Update rules.md

**Files:**
- Modify: `plugins/ctx7-docs-lookup/hooks/rules.md`

- [ ] **Step 1: Replace rules.md with mode-neutral version**

```markdown
The same error has occurred 2 or more times. Stop guessing and consult official documentation.

## Immediate Actions
1. Check the exact version of the relevant library in package.json (or equivalent dependency file)
2. Query official docs via context7 (follow the method specified by $CTX7_MODE in the ctx7-docs-lookup skill)
3. Use version-specific library IDs when available (e.g., /vercel/next.js/v15.1.8)
4. If the first query is insufficient, retry with different keywords 2-3 more times

## Query Strategy
- 1st: Search directly using key terms from the error message
- 2nd: Broaden to related concepts or feature categories
- 3rd: Search for new/changed APIs in the current version

## Do NOT
- Retry the same approach repeatedly
- Rely solely on training data for guesses
- Write code based on "it will probably work" without checking docs
```

- [ ] **Step 2: Commit**

```bash
git add plugins/ctx7-docs-lookup/hooks/rules.md
git commit -m "refactor: make rules.md mode-neutral for dual ctx7 access"
```

---

### Task 4: Update SKILL.md

**Files:**
- Modify: `plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md`

- [ ] **Step 1: Update frontmatter description to be mode-neutral**

In the YAML frontmatter (line 3), replace `Forces the use of ctx7 (context7 MCP) to consult official documentation.` with `Forces the use of ctx7 (context7) to consult official documentation.` — removes the MCP-only framing.

- [ ] **Step 2: Replace the "How to Use context7" section**

Two edits are needed to preserve `### Step 0` while replacing the surrounding content:

**Edit A:** Replace lines 65-76 (from `## How to Use context7` heading through the paragraph ending before `### Step 0`). This removes the old table-based access method list. Replace with the new conditional content below.

**Edit B:** Delete lines 86-93 (`### Lookup Workflow` and its 4 bullet points). The lookup workflow steps are now embedded within each mode's subsection above.

**Result:** `### Step 0: Understand the Project First` (lines 77-85) remains in place, now appearing after the three new mode subsections.

**Edit A replacement content:**

```markdown
## How to Use context7

The `$CTX7_MODE` environment variable is automatically set at session start. Check its value and follow the corresponding path below.

### If `CTX7_MODE=mcp` — MCP Tools Available

Use MCP tools directly:

1. **Resolve the library ID** — call `mcp__context7__resolve-library-id` with the library name (e.g., "nextjs", "react", "prisma")
2. **Query the documentation** — call `mcp__context7__query-docs` with the resolved library ID and a detailed, descriptive topic. Include version number and project context in your query when relevant.
3. **Evaluate the results** — check whether the docs confirm your approach or reveal a better/newer API.
4. **If results are insufficient, query again with different keywords** — try at least 2-3 different queries before concluding that the information isn't available.

### If `CTX7_MODE=skill` — Use CLI/Skill

MCP is not configured. Use the `find-docs` skill instead:

1. **Invoke the skill** — call the `find-docs` skill via the Skill tool with the library name and topic as arguments.
2. **Evaluate the results** — same as MCP path: verify the docs match your use case.
3. **If results are insufficient, invoke again with different keywords** — rephrase, broaden, or narrow your search terms.

### If `CTX7_MODE=unknown` or Not Set — Fallback

The detection could not determine which method is available. Try in this order:

1. **Try MCP first** — call `mcp__context7__resolve-library-id`. If it succeeds, continue with MCP tools.
2. **If MCP fails** (tool not found / unknown tool error), **try the skill** — invoke `find-docs` via the Skill tool.
3. **If both fail**, inform the user: "context7 is not available. Add a context7 MCP server to .mcp.json, or install a plugin that provides the find-docs skill."
```

- [ ] **Step 3: Verify the full SKILL.md reads correctly**

Run: Read the updated SKILL.md and verify section flow: Why → When NOT → Trigger Conditions → How to Use (updated with 3 mode subsections) → Step 0: Understand the Project First (preserved) → Important Notes → References

- [ ] **Step 4: Commit**

```bash
git add plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md
git commit -m "feat: update SKILL.md with CTX7_MODE conditional instructions"
```
