# Plugin Conversion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert skill.md repo into a `brain1401/claude-plugins` marketplace repo with 4 independent plugins, 3 of which have hybrid Skill + Hook architecture.

**Architecture:** Single marketplace repo with `plugins/` containing 4 self-contained plugins. Each plugin has `.claude-plugin/plugin.json`, `skills/`, and optionally `hooks/`. marketplace.json at repo root references plugins via relative paths.

**Tech Stack:** Claude Code plugin system, Bash (hook scripts), Python 3 (hook scripts), JSON (configuration), Markdown (skills)

**Spec:** `docs/superpowers/specs/2026-03-24-plugin-conversion-design.md`

---

## File Map

**Create:**
- `.claude-plugin/marketplace.json` — marketplace catalog
- `plugins/korean-commit-message/.claude-plugin/plugin.json` — plugin manifest
- `plugins/korean-commit-message/hooks/hooks.json` — PreToolUse hook config
- `plugins/korean-commit-message/hooks/inject_rules.sh` — commit rules injection script
- `plugins/korean-code-comments/.claude-plugin/plugin.json` — plugin manifest
- `plugins/korean-code-comments/hooks/hooks.json` — PostToolUse hook config
- `plugins/korean-code-comments/hooks/remind_comments.py` — session-once reminder script
- `plugins/korean-code-comments/hooks/rules.md` — comment style rules
- `plugins/ctx7-docs-lookup/.claude-plugin/plugin.json` — plugin manifest
- `plugins/ctx7-docs-lookup/hooks/hooks.json` — PostToolUse hook config
- `plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py` — error tracking script
- `plugins/ctx7-docs-lookup/hooks/rules.md` — ctx7 lookup rules
- `plugins/activity-state/.claude-plugin/plugin.json` — plugin manifest

**Move (existing → new):**
- `skills/korean-commit-message/SKILL.md` → `plugins/korean-commit-message/skills/korean-commit-message/SKILL.md`
- `skills/korean-code-comments/SKILL.md` → `plugins/korean-code-comments/skills/korean-code-comments/SKILL.md`
- `skills/ctx7-docs-lookup/SKILL.md` → `plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md`
- `skills/activity-state/SKILL.md` → `plugins/activity-state/skills/activity-state/SKILL.md`
- `skills/activity-state/references/activity-behavior.md` → `plugins/activity-state/skills/activity-state/references/activity-behavior.md`

**Rewrite:**
- `README.md` — marketplace installation instructions

**Delete:**
- `skills/` directory (after files moved)
- `docs/superpowers/` directory (specs/plans no longer needed in final repo)

---

### Task 1: Create marketplace and plugin directory structure

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `plugins/korean-commit-message/.claude-plugin/plugin.json`
- Create: `plugins/korean-code-comments/.claude-plugin/plugin.json`
- Create: `plugins/ctx7-docs-lookup/.claude-plugin/plugin.json`
- Create: `plugins/activity-state/.claude-plugin/plugin.json`

- [ ] **Step 1: Create marketplace.json**

```json
{
  "name": "claude-plugins",
  "owner": { "name": "brain1401" },
  "plugins": [
    {
      "name": "korean-commit-message",
      "description": "Korean conventional commit 메시지 규칙 적용 (Skill + Hook)",
      "source": "./plugins/korean-commit-message"
    },
    {
      "name": "korean-code-comments",
      "description": "코드 작성/수정 시 복잡한 로직에 한국어 주석 작성 (Skill + Hook)",
      "source": "./plugins/korean-code-comments"
    },
    {
      "name": "ctx7-docs-lookup",
      "description": "반복 오류 시 ctx7로 공식 문서 참조 강제 (Skill + Hook)",
      "source": "./plugins/ctx7-docs-lookup"
    },
    {
      "name": "activity-state",
      "description": "Next.js cacheComponents 환경에서 React Activity 상태 버그 방지",
      "source": "./plugins/activity-state"
    }
  ]
}
```

Write to `.claude-plugin/marketplace.json`.

- [ ] **Step 2: Create korean-commit-message plugin.json**

```json
{
  "name": "korean-commit-message",
  "version": "1.0.0",
  "description": "Korean conventional commit 메시지 규칙 적용 및 자동 검증",
  "author": { "name": "brain1401" }
}
```

Write to `plugins/korean-commit-message/.claude-plugin/plugin.json`.

- [ ] **Step 3: Create korean-code-comments plugin.json**

```json
{
  "name": "korean-code-comments",
  "version": "1.0.0",
  "description": "코드 작성/수정 시 복잡한 로직에 한국어 주석 자동 작성",
  "author": { "name": "brain1401" }
}
```

Write to `plugins/korean-code-comments/.claude-plugin/plugin.json`.

- [ ] **Step 4: Create ctx7-docs-lookup plugin.json**

```json
{
  "name": "ctx7-docs-lookup",
  "version": "1.0.0",
  "description": "반복 오류 시 ctx7로 공식 문서 참조 강제",
  "author": { "name": "brain1401" }
}
```

Write to `plugins/ctx7-docs-lookup/.claude-plugin/plugin.json`.

- [ ] **Step 5: Create activity-state plugin.json**

```json
{
  "name": "activity-state",
  "version": "1.0.0",
  "description": "Next.js cacheComponents 환경에서 React Activity 상태 버그 방지",
  "author": { "name": "brain1401" }
}
```

Write to `plugins/activity-state/.claude-plugin/plugin.json`.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/ plugins/*/.claude-plugin/
git commit -m "feat: 마켓플레이스 및 플러그인 매니페스트 생성"
```

---

### Task 2: Move existing skills into plugin directories

**Files:**
- Move: `skills/korean-commit-message/SKILL.md` → `plugins/korean-commit-message/skills/korean-commit-message/SKILL.md`
- Move: `skills/korean-code-comments/SKILL.md` → `plugins/korean-code-comments/skills/korean-code-comments/SKILL.md`
- Move: `skills/ctx7-docs-lookup/SKILL.md` → `plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md`
- Move: `skills/activity-state/SKILL.md` → `plugins/activity-state/skills/activity-state/SKILL.md`
- Move: `skills/activity-state/references/activity-behavior.md` → `plugins/activity-state/skills/activity-state/references/activity-behavior.md`
- Delete: `skills/` (empty after moves)

- [ ] **Step 1: Create target directories and move files**

```bash
# korean-commit-message
mkdir -p plugins/korean-commit-message/skills/korean-commit-message
mv skills/korean-commit-message/SKILL.md plugins/korean-commit-message/skills/korean-commit-message/SKILL.md

# korean-code-comments
mkdir -p plugins/korean-code-comments/skills/korean-code-comments
mv skills/korean-code-comments/SKILL.md plugins/korean-code-comments/skills/korean-code-comments/SKILL.md

# ctx7-docs-lookup
mkdir -p plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup
mv skills/ctx7-docs-lookup/SKILL.md plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md

# activity-state (with references subdirectory)
mkdir -p plugins/activity-state/skills/activity-state/references
mv skills/activity-state/SKILL.md plugins/activity-state/skills/activity-state/SKILL.md
mv skills/activity-state/references/activity-behavior.md plugins/activity-state/skills/activity-state/references/activity-behavior.md
```

- [ ] **Step 2: Remove empty skills directory**

```bash
rm -rf skills/
```

- [ ] **Step 3: Verify all SKILL.md files are in place**

```bash
find plugins -name "SKILL.md" -o -name "activity-behavior.md" | sort
```

Expected output:
```
plugins/activity-state/skills/activity-state/SKILL.md
plugins/activity-state/skills/activity-state/references/activity-behavior.md
plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md
plugins/korean-code-comments/skills/korean-code-comments/SKILL.md
plugins/korean-commit-message/skills/korean-commit-message/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: 기존 스킬 파일을 플러그인 디렉토리 구조로 이동"
```

---

### Task 3: Implement korean-commit-message hooks

**Files:**
- Create: `plugins/korean-commit-message/hooks/hooks.json`
- Create: `plugins/korean-commit-message/hooks/inject_rules.sh`

- [ ] **Step 1: Create hooks.json**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/inject_rules.sh",
            "timeout": 5
          },
          {
            "type": "prompt",
            "prompt": "Check if this bash command contains 'git commit'. If it does NOT contain 'git commit', return 'approve' immediately without any checks. If it DOES contain 'git commit', validate the commit message format. Required format: '<type>: <subject>' where type is one of (feat|fix|docs|style|refactor|test|chore|perf|build|ci), subject is 50 chars or fewer, starts with uppercase letter, no trailing period, imperative mood. Both Korean and English subjects are acceptable. If the format is wrong, return 'deny' with the corrected message suggestion. If format is correct, return 'approve'.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Write to `plugins/korean-commit-message/hooks/hooks.json`.

- [ ] **Step 2: Create inject_rules.sh** (requires `jq` on PATH)

```bash
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
```

Write to `plugins/korean-commit-message/hooks/inject_rules.sh` and make executable.

- [ ] **Step 3: Make script executable**

```bash
chmod +x plugins/korean-commit-message/hooks/inject_rules.sh
```

- [ ] **Step 4: Test inject_rules.sh locally**

Test with git commit command:
```bash
echo '{"tool_input": {"command": "git commit -m \"feat: Add feature\""}}' | bash plugins/korean-commit-message/hooks/inject_rules.sh
echo "Exit code: $?"
```

Expected: JSON output with `hookSpecificOutput` and `systemMessage`, exit code 0.

Test with non-commit command:
```bash
echo '{"tool_input": {"command": "ls -la"}}' | bash plugins/korean-commit-message/hooks/inject_rules.sh
echo "Exit code: $?"
```

Expected: no output, exit code 0.

- [ ] **Step 5: Commit**

```bash
git add plugins/korean-commit-message/hooks/
git commit -m "feat: korean-commit-message 플러그인 PreToolUse 훅 구현"
```

---

### Task 4: Implement korean-code-comments hooks

**Files:**
- Create: `plugins/korean-code-comments/hooks/hooks.json`
- Create: `plugins/korean-code-comments/hooks/remind_comments.py`
- Create: `plugins/korean-code-comments/hooks/rules.md`

- [ ] **Step 1: Create hooks.json**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/remind_comments.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Write to `plugins/korean-code-comments/hooks/hooks.json`.

- [ ] **Step 2: Create rules.md**

```markdown
이 세션에서 코드를 수정하고 있습니다. 복잡한 로직에 한국어 주석을 추가하세요.

## 주석 작성 기준
- 복잡한 비즈니스 로직, 도메인 지식이 필요한 부분
- 다단계 알고리즘, 데이터 변환
- 의도가 코드만으로 파악 안 되는 우회 처리, 엣지 케이스
- 자명한 코드에는 주석 불필요

## 스타일 규칙
- 존댓말 금지. 명사형 종결 사용
  - (X) 파일이 없으면 생성함
  - (O) 파일 부재 시 생성
- 콜론(:) 금지. 괄호나 조사로 대체
  - (X) 기본값: 30초
  - (O) 기본값 30초 / 기본값(30초)
- em dash(—) 금지. 괄호, 쉼표, 문장 재구성으로 대체
  - (X) 재고 확인 — 품절 시 중단
  - (O) 재고 확인 (품절 시 중단)
- 번호는 1. 2. 3. 형식만 사용
- '사용자', '요청' 등 AI 저작 흔적 단어 금지 (소프트웨어 최종 사용자 지칭 시 예외)
```

Write to `plugins/korean-code-comments/hooks/rules.md`.

- [ ] **Step 3: Create remind_comments.py**

```python
#!/usr/bin/env python3
"""세션당 1회 한국어 주석 규칙 리마인드 (PostToolUse hook)."""

import json
import os
import sys
from pathlib import Path

CODE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".go", ".rs",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".kt", ".swift",
}


def get_file_paths(data: dict) -> list[str]:
    """Write/Edit/MultiEdit에서 편집된 파일 경로 추출."""
    tool_input = data.get("tool_input", {})

    # Write, Edit
    file_path = tool_input.get("file_path")
    if file_path:
        return [file_path]

    # MultiEdit
    files_to_edit = tool_input.get("files_to_edit", [])
    return [f.get("file_path", "") for f in files_to_edit if f.get("file_path")]


def is_code_file(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in CODE_EXTENSIONS


def main() -> None:
    data = json.load(sys.stdin)
    session_id = data.get("session_id", "unknown")

    # 코드 파일 편집 여부 확인
    file_paths = get_file_paths(data)
    if not any(is_code_file(fp) for fp in file_paths):
        sys.exit(0)

    # 세션당 1회 체크
    state_file = Path(f"/tmp/claude_comments_reminded_{session_id}")
    if state_file.exists():
        sys.exit(0)

    # 상태 저장
    state_file.touch()

    # rules.md 읽어서 systemMessage로 출력
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    rules_path = Path(plugin_root) / "hooks" / "rules.md"

    if rules_path.exists():
        rules_content = rules_path.read_text(encoding="utf-8")
    else:
        rules_content = "복잡한 로직에 한국어 주석을 추가하세요."

    output = json.dumps({"systemMessage": rules_content}, ensure_ascii=False)
    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

Write to `plugins/korean-code-comments/hooks/remind_comments.py` and make executable.

- [ ] **Step 4: Make script executable**

```bash
chmod +x plugins/korean-code-comments/hooks/remind_comments.py
```

- [ ] **Step 5: Test remind_comments.py locally**

First invocation (should output systemMessage):
```bash
echo '{"session_id": "test123", "tool_input": {"file_path": "/tmp/test.ts"}}' | \
  CLAUDE_PLUGIN_ROOT="plugins/korean-code-comments" \
  python3 plugins/korean-code-comments/hooks/remind_comments.py
echo "Exit code: $?"
```

Expected: JSON with systemMessage containing rules, exit code 0.

Second invocation with same session_id (should be silent):
```bash
echo '{"session_id": "test123", "tool_input": {"file_path": "/tmp/test.ts"}}' | \
  CLAUDE_PLUGIN_ROOT="plugins/korean-code-comments" \
  python3 plugins/korean-code-comments/hooks/remind_comments.py
echo "Exit code: $?"
```

Expected: no output, exit code 0.

Non-code file (should be silent):
```bash
echo '{"session_id": "test456", "tool_input": {"file_path": "/tmp/test.md"}}' | \
  CLAUDE_PLUGIN_ROOT="plugins/korean-code-comments" \
  python3 plugins/korean-code-comments/hooks/remind_comments.py
echo "Exit code: $?"
```

Expected: no output, exit code 0.

Clean up test state:
```bash
rm -f /tmp/claude_comments_reminded_test123
```

- [ ] **Step 6: Commit**

```bash
git add plugins/korean-code-comments/hooks/
git commit -m "feat: korean-code-comments 플러그인 PostToolUse 훅 구현"
```

---

### Task 5: Implement ctx7-docs-lookup hooks

**Files:**
- Create: `plugins/ctx7-docs-lookup/hooks/hooks.json`
- Create: `plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py`
- Create: `plugins/ctx7-docs-lookup/hooks/rules.md`

- [ ] **Step 1: Create hooks.json**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/detect_repeated_errors.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Write to `plugins/ctx7-docs-lookup/hooks/hooks.json`.

- [ ] **Step 2: Create rules.md**

```markdown
동일한 오류가 2회 이상 반복되고 있습니다. 추측으로 계속 시도하지 마세요.

## 즉시 수행할 것
1. 프로젝트의 package.json (또는 의존성 파일)에서 관련 라이브러리의 정확한 버전 확인
2. ctx7 MCP로 해당 라이브러리의 공식 문서 조회 (mcp__context7__resolve-library-id → mcp__context7__query-docs)
3. 버전별 library ID가 있으면 사용 (예: /vercel/next.js/v15.1.8)
4. 첫 쿼리로 부족하면 키워드를 바꿔서 2-3회 추가 쿼리

## 쿼리 전략
- 1차: 에러 메시지의 핵심 키워드로 직접 검색
- 2차: 관련 개념이나 기능 카테고리로 확장
- 3차: 해당 버전의 신규/변경 API 검색

## 하지 말 것
- 같은 접근을 반복 시도
- 훈련 데이터에만 의존한 추측
- 문서 확인 없이 "아마 될 것" 식의 코드 작성
```

Write to `plugins/ctx7-docs-lookup/hooks/rules.md`.

- [ ] **Step 3: Create detect_repeated_errors.py**

```python
#!/usr/bin/env python3
"""반복 에러 감지 후 ctx7 공식 문서 참조 리마인드 (PostToolUse hook)."""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ERROR_PATTERNS = re.compile(
    r"(?i)\b(error|exception|traceback|FAILED|panic)\b"
)

# 정규화 시 제거할 패턴 (파일 경로, 줄 번호, 숫자값)
NORMALIZE_PATTERNS = [
    re.compile(r"(/[\w./-]+)"),          # 파일 경로
    re.compile(r"\b\d+\b"),              # 숫자값 (줄 번호 포함)
    re.compile(r"0x[0-9a-fA-F]+"),       # 16진수 주소
]


def extract_error_signature(text: str) -> str | None:
    """에러 메시지에서 정규화된 시그니처 해시 생성."""
    if not ERROR_PATTERNS.search(text):
        return None

    # 에러 타입/클래스 + 첫 번째 줄 추출
    lines = text.strip().splitlines()
    error_lines = [
        line.strip() for line in lines
        if ERROR_PATTERNS.search(line)
    ]

    if not error_lines:
        return None

    # 첫 번째 에러 줄만 사용
    signature = error_lines[0]

    # 정규화 (경로, 숫자 제거)
    for pattern in NORMALIZE_PATTERNS:
        signature = pattern.sub("", signature)

    # 공백 정규화
    signature = re.sub(r"\s+", " ", signature).strip()

    if not signature:
        return None

    return hashlib.sha256(signature.encode()).hexdigest()


def main() -> None:
    data = json.load(sys.stdin)
    session_id = data.get("session_id", "unknown")
    tool_result = data.get("tool_result", "")

    if isinstance(tool_result, dict):
        tool_result = json.dumps(tool_result)

    # 에러 시그니처 생성
    signature = extract_error_signature(str(tool_result))
    if signature is None:
        sys.exit(0)

    # 세션별 에러 추적 파일
    tracking_path = Path(f"/tmp/claude_error_tracking_{session_id}.json")

    if tracking_path.exists():
        tracking = json.loads(tracking_path.read_text(encoding="utf-8"))
    else:
        tracking = {}

    # 카운트 업데이트
    count = tracking.get(signature, 0) + 1
    tracking[signature] = count
    tracking_path.write_text(
        json.dumps(tracking, ensure_ascii=False), encoding="utf-8"
    )

    # 2회 미만이면 스킵
    if count < 2:
        sys.exit(0)

    # 2회 이상: rules.md 주입 + 카운터 리셋
    tracking[signature] = 0
    tracking_path.write_text(
        json.dumps(tracking, ensure_ascii=False), encoding="utf-8"
    )

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    rules_path = Path(plugin_root) / "hooks" / "rules.md"

    if rules_path.exists():
        rules_content = rules_path.read_text(encoding="utf-8")
    else:
        rules_content = "동일 오류 반복 감지. ctx7으로 공식 문서를 확인하세요."

    output = json.dumps({"systemMessage": rules_content}, ensure_ascii=False)
    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
```

Write to `plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py` and make executable.

- [ ] **Step 4: Make script executable**

```bash
chmod +x plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py
```

- [ ] **Step 5: Test detect_repeated_errors.py locally**

First error (count=1, should be silent):
```bash
echo '{"session_id": "test789", "tool_input": {"command": "npm run build"}, "tool_result": "Error: Cannot find module react"}' | \
  CLAUDE_PLUGIN_ROOT="plugins/ctx7-docs-lookup" \
  python3 plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py
echo "Exit code: $?"
```

Expected: no output, exit code 0.

Second same error (count=2, should trigger):
```bash
echo '{"session_id": "test789", "tool_input": {"command": "npm run build"}, "tool_result": "Error: Cannot find module react"}' | \
  CLAUDE_PLUGIN_ROOT="plugins/ctx7-docs-lookup" \
  python3 plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py
echo "Exit code: $?"
```

Expected: JSON with systemMessage containing rules, exit code 0.

Third same error (count reset to 0, then incremented to 1, should be silent):
```bash
echo '{"session_id": "test789", "tool_input": {"command": "npm run build"}, "tool_result": "Error: Cannot find module react"}' | \
  CLAUDE_PLUGIN_ROOT="plugins/ctx7-docs-lookup" \
  python3 plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py
echo "Exit code: $?"
```

Expected: no output, exit code 0.

Non-error (should be silent):
```bash
echo '{"session_id": "test789", "tool_input": {"command": "ls"}, "tool_result": "file1.txt\nfile2.txt"}' | \
  CLAUDE_PLUGIN_ROOT="plugins/ctx7-docs-lookup" \
  python3 plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py
echo "Exit code: $?"
```

Expected: no output, exit code 0.

Clean up test state:
```bash
rm -f /tmp/claude_error_tracking_test789.json
```

- [ ] **Step 6: Commit**

```bash
git add plugins/ctx7-docs-lookup/hooks/
git commit -m "feat: ctx7-docs-lookup 플러그인 PostToolUse 훅 구현"
```

---

### Task 6: Rewrite README.md and clean up

**Files:**
- Rewrite: `README.md`
- Delete: `docs/` directory

- [ ] **Step 1: Write new README.md**

```markdown
# claude-plugins

brain1401의 Claude Code 플러그인 마켓플레이스

## Plugins

| Plugin | Description | Hook |
| --- | --- | --- |
| [korean-commit-message](plugins/korean-commit-message/) | Korean conventional commit 메시지 규칙 적용 및 자동 검증 | PreToolUse (Bash) |
| [korean-code-comments](plugins/korean-code-comments/) | 코드 작성/수정 시 복잡한 로직에 한국어 주석 자동 작성 | PostToolUse (Write/Edit) |
| [ctx7-docs-lookup](plugins/ctx7-docs-lookup/) | 반복 오류 시 ctx7로 공식 문서 참조 강제 | PostToolUse (Bash) |
| [activity-state](plugins/activity-state/) | Next.js cacheComponents 환경에서 React Activity 상태 버그 방지 | - |

## Install

```bash
# 마켓플레이스 등록
/plugin marketplace add brain1401/claude-plugins

# 개별 플러그인 설치
/plugin install korean-commit-message@claude-plugins
/plugin install korean-code-comments@claude-plugins
/plugin install ctx7-docs-lookup@claude-plugins
/plugin install activity-state@claude-plugins
```

## Architecture

각 플러그인은 **Skill + Hook 하이브리드** 구조:

- **Skill**: Claude가 작업 시작 시 로드. 상세 규칙, 패턴, 예시를 포함한 완전한 가이드 제공
- **Hook**: 특정 이벤트 발생 시 자동 실행. 검증 또는 핵심 규칙 리마인드

둘은 독립적인 이중 안전장치로, Skill이 invoke되지 않아도 Hook이 핵심 규칙을 보장합니다.
```

Write to `README.md` (overwrite existing).

- [ ] **Step 2: Delete docs directory**

```bash
rm -rf docs/
```

- [ ] **Step 3: Verify final directory structure**

```bash
find . -not -path './.git/*' -not -path './.git' -type f | sort
```

Expected:
```
./.claude-plugin/marketplace.json
./.gitignore
./plugins/activity-state/.claude-plugin/plugin.json
./plugins/activity-state/skills/activity-state/references/activity-behavior.md
./plugins/activity-state/skills/activity-state/SKILL.md
./plugins/ctx7-docs-lookup/.claude-plugin/plugin.json
./plugins/ctx7-docs-lookup/hooks/detect_repeated_errors.py
./plugins/ctx7-docs-lookup/hooks/hooks.json
./plugins/ctx7-docs-lookup/hooks/rules.md
./plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md
./plugins/korean-code-comments/.claude-plugin/plugin.json
./plugins/korean-code-comments/hooks/hooks.json
./plugins/korean-code-comments/hooks/remind_comments.py
./plugins/korean-code-comments/hooks/rules.md
./plugins/korean-code-comments/skills/korean-code-comments/SKILL.md
./plugins/korean-commit-message/.claude-plugin/plugin.json
./plugins/korean-commit-message/hooks/hooks.json
./plugins/korean-commit-message/hooks/inject_rules.sh
./plugins/korean-commit-message/skills/korean-commit-message/SKILL.md
./README.md
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "docs: README 갱신 및 기존 docs 디렉토리 정리"
```

---

### Task 7: Create remote repository and push

- [ ] **Step 1: Create GitHub repository `brain1401/claude-plugins`**

User creates `brain1401/claude-plugins` on GitHub (public repo, no README/license/gitignore).

- [ ] **Step 2: Update git remote**

```bash
git remote set-url origin git@github.com:brain1401/claude-plugins.git
```

- [ ] **Step 3: Push to remote**

```bash
git push -u origin main
```

- [ ] **Step 4: Verify marketplace works**

In a fresh Claude Code session:
```
/plugin marketplace add brain1401/claude-plugins
```

Should show 4 available plugins. Install one to verify:
```
/plugin install korean-commit-message@claude-plugins
```
