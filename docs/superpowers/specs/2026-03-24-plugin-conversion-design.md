# Plugin Conversion Design: skill.md → claude-plugins

## Overview

skill.md 레포지토리를 단일 마켓플레이스 레포 `brain1401/claude-plugins`로 전환한다. 4개의 기존 스킬을 각각 독립 플러그인으로 분리하고, Hook이 필요한 3개 플러그인에는 Skill + Hook 하이브리드 구조를 적용한다.

## Repository Structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── korean-commit-message/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   │   └── korean-commit-message/
│   │   │       └── SKILL.md
│   │   └── hooks/
│   │       ├── hooks.json
│   │       └── inject_rules.sh
│   │
│   ├── korean-code-comments/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   │   └── korean-code-comments/
│   │   │       └── SKILL.md
│   │   └── hooks/
│   │       ├── hooks.json
│   │       ├── remind_comments.py
│   │       └── rules.md
│   │
│   ├── ctx7-docs-lookup/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   │   └── ctx7-docs-lookup/
│   │   │       └── SKILL.md
│   │   └── hooks/
│   │       ├── hooks.json
│   │       ├── detect_repeated_errors.py
│   │       └── rules.md
│   │
│   └── activity-state/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── activity-state/
│               ├── SKILL.md
│               └── references/
│                   └── activity-behavior.md
├── README.md
└── .gitignore
```

## Marketplace Configuration

### `.claude-plugin/marketplace.json`

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

## Plugin Manifests

각 플러그인의 `.claude-plugin/plugin.json`:

| Plugin | name | description |
|--------|------|-------------|
| korean-commit-message | `korean-commit-message` | Korean conventional commit 메시지 규칙 적용 및 자동 검증 |
| korean-code-comments | `korean-code-comments` | 코드 작성/수정 시 복잡한 로직에 한국어 주석 자동 작성 |
| ctx7-docs-lookup | `ctx7-docs-lookup` | 반복 오류 시 ctx7로 공식 문서 참조 강제 |
| activity-state | `activity-state` | Next.js cacheComponents 환경에서 React Activity 상태 버그 방지 |

모든 plugin.json의 공통 필드:

- `version`: `"1.0.0"`
- `author`: `{ "name": "brain1401" }`

## Hook Design

### Design Principle: Skill과 Hook의 역할 분담

- **Skill**: Claude가 작업을 시작할 때 로드됨. 상세 규칙, 패턴, 예시를 포함한 완전한 가이드 제공
- **Hook**: 특정 이벤트 발생 시 자동 실행. 검증 또는 핵심 규칙 리마인드

둘은 체인이 아니라 독립적인 이중 안전장치. Hook이 Skill을 invoke할 필요 없음.

---

### Plugin 1: korean-commit-message

**Hook 전략**: PreToolUse (Bash) — command hook + prompt hook 병렬 실행

- **command hook**: `inject_rules.sh`가 축약 규칙을 systemMessage로 주입 (exit 0)
- **prompt hook**: git commit 명령을 감지하여 메시지 포맷 검증 → approve/deny

**`hooks/hooks.json`:**

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

**`hooks/inject_rules.sh`:**

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

---

### Plugin 2: korean-code-comments

**Hook 전략**: PostToolUse (Write|Edit|MultiEdit) — command hook

- 코드 파일 편집 시 세션당 1회 rules.md를 읽어서 systemMessage로 주입

**`hooks/hooks.json`:**

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

**`hooks/remind_comments.py`** 동작:

1. stdin에서 `session_id`, `tool_input` 파싱
   - Write/Edit: `tool_input.file_path`
   - MultiEdit: `tool_input.files_to_edit[].file_path`
2. 편집된 파일이 코드 파일인지 확인 (확장자 기반: `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.java`, `.go`, `.rs`, `.c`, `.cpp`, `.h`, `.hpp`, `.cs`, `.kt`, `.swift`)
3. 코드 파일이 아니면 `exit(0)`
4. 세션별 상태 파일 (`/tmp/claude_comments_reminded_{session_id}`) 확인
5. 이미 리마인드했으면 `exit(0)`
6. 첫 코드 편집이면 상태 파일 저장 후 `${CLAUDE_PLUGIN_ROOT}/hooks/rules.md`를 읽어서 JSON `systemMessage`로 stdout 출력 → `exit(0)`

**`hooks/rules.md`:**

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

---

### Plugin 3: ctx7-docs-lookup

**Hook 전략**: PostToolUse (Bash) — command hook

- Bash 실행 후 에러 감지, 동일 에러 2회 이상 반복 시 rules.md를 systemMessage로 주입

**`hooks/hooks.json`:**

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

**`hooks/detect_repeated_errors.py`** 동작:

1. stdin에서 `session_id`, `tool_input`, `tool_result` 파싱
2. `tool_result`에서 에러 감지 (exit code 비정상, stderr에 에러 패턴: `error`, `Error`, `ERROR`, `traceback`, `Exception`, `FAILED`, `panic`)
3. 에러가 아니면 `exit(0)`
4. 에러 시그니처 생성 (정규화 전략):
   - 에러 메시지에서 파일 경로, 줄 번호, 숫자값 제거 (정규식으로 치환)
   - 에러 타입/클래스 + 첫 번째 줄 메시지만 추출
   - 정규화된 문자열의 SHA-256 해시 생성
   - "동일 에러" = 해시 완전 일치
5. 세션별 에러 추적 파일 (`/tmp/claude_error_tracking_{session_id}.json`) 에 기록
6. 동일 에러가 2회 미만이면 `exit(0)`
7. 2회 이상이면 `${CLAUDE_PLUGIN_ROOT}/hooks/rules.md`를 읽어서 JSON `systemMessage`로 stdout 출력 → `exit(0)`
8. 리마인드 후 해당 에러 카운터 리셋 (같은 에러 반복 시 다시 트리거)

**`hooks/rules.md`:**

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

---

### Plugin 4: activity-state

**Hook 없음.** Skill 전용. 기존 SKILL.md와 references/activity-behavior.md를 그대로 이동.

## Hook Summary

| Plugin | Hook Event | Hook Type | Trigger | 동작 |
|--------|-----------|-----------|---------|------|
| korean-commit-message | PreToolUse (Bash) | command + prompt (병렬) | git commit 명령 감지 | command: 규칙 주입, prompt: 포맷 검증 |
| korean-code-comments | PostToolUse (Write\|Edit\|MultiEdit) | command (Python) | 세션 첫 코드 편집 | rules.md → systemMessage 주입 (1회) |
| ctx7-docs-lookup | PostToolUse (Bash) | command (Python) | 에러 2회 이상 반복 | rules.md → systemMessage 주입 (리셋 후 재트리거) |
| activity-state | — | — | — | — |

## Skills (변경 없음)

기존 SKILL.md 파일은 내용 변경 없이 플러그인 디렉토리로 이동. description과 frontmatter 유지.

## Migration Steps

1. 레포 이름을 `claude-plugins`로 변경 (원격 레포 재생성)
2. 기존 `skills/` 디렉토리 구조를 `plugins/` 구조로 재배치
3. `.claude-plugin/marketplace.json` 생성
4. 각 플러그인의 `.claude-plugin/plugin.json` 생성
5. 각 플러그인의 `hooks/hooks.json` 및 hook 스크립트 생성
6. `hooks/rules.md` 작성
7. README.md 갱신
8. 기존 skills/ 디렉토리 및 관련 파일 제거
9. 테스트 (`claude --debug`)

## Installation

```bash
# 마켓플레이스 등록
/plugin marketplace add brain1401/claude-plugins

# 개별 플러그인 설치
/plugin install korean-commit-message@claude-plugins
/plugin install korean-code-comments@claude-plugins
/plugin install ctx7-docs-lookup@claude-plugins
/plugin install activity-state@claude-plugins
```
