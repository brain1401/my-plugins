#!/bin/bash
set -euo pipefail

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# git commit 명령이 아니면 스킵
if [[ "$command" != *"git commit"* ]]; then
  exit 0
fi

# 축약 규칙 주입 (permissionDecision: allow로 실행 허용 + systemMessage로 규칙 컨텍스트 주입)
cat <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "allow"
  },
  "systemMessage": "커밋 메시지 규칙 리마인드:\n- 형식: <type>: <subject>\n- type: feat|fix|docs|style|refactor|test|chore|perf|build|ci\n- subject: 50자 이하, 대문자 시작, 마침표 없음, 명령형\n- 한국어 subject 권장\n- body: 선택사항, subject로 부족할 때만. 72자 줄바꿈. what/why 설명\n- footer: 선택사항. BREAKING CHANGE 또는 이슈 참조 (Closes #123)\n\n좋은 예:\n  feat: 사용자 로그인 기능 추가\n  fix: 로그인 오류 수정\n  docs: Update API documentation\n\n나쁜 예:\n  feat: added user login feature. (소문자, 마침표, 과거형)"
}
EOF
