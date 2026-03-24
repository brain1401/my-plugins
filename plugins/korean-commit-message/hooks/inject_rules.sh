#!/bin/bash
set -euo pipefail

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Skip if not a git commit command
if [[ "$command" != *"git commit"* ]]; then
  exit 0
fi

# Inject commit rules (permissionDecision: allow + systemMessage for context)
cat <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "allow"
  },
  "systemMessage": "Commit message rules reminder:\n- Format: <type>: <subject>\n- type: feat|fix|docs|style|refactor|test|chore|perf|build|ci\n- subject: 50 chars or fewer, starts with uppercase, no trailing period, imperative mood\n- Korean subject preferred\n- body: optional, only when subject is insufficient. Wrap at 72 chars. Explain what/why.\n- footer: optional. BREAKING CHANGE or issue refs (Closes #123)\n\nGood examples:\n  feat: 사용자 로그인 기능 추가\n  fix: 로그인 오류 수정\n  docs: Update API documentation\n\nBad examples:\n  feat: added user login feature. (lowercase, trailing period, past tense)"
}
EOF
