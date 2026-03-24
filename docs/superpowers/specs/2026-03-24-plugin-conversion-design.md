# Plugin Conversion Design: skill.md → claude-plugins

## Overview

기존 `brain1401/skill.md` 스킬 전용 저장소를 `brain1401/claude-plugins` 마켓플레이스 저장소로 전환한다. 4개 스킬을 개별 플러그인으로 분리하고, 3개 플러그인에 Hook을 추가하여 하이브리드(Skill + Hook) 구조를 구현한다.

## Decisions

| 항목 | 결정 |
|------|------|
| 레포 이름 | `brain1401/claude-plugins` |
| 배포 방식 | 마켓플레이스 (marketplace.json) |
| 플러그인 분리 | 스킬당 1 플러그인 (4개) |
| 플러그인 배치 | 단일 레포 내 `plugins/` 디렉토리 |
| Hook-Skill 관계 | 독립적 이중 안전장치 (체이닝 없음) |
| Hook 콘텐츠 관리 | `hooks/rules.md` 파일을 스크립트가 읽어서 출력 |

## Plugin Configuration

| 플러그인 | Skill | Hook | Hook 이벤트 | Hook 타입 |
|----------|-------|------|-------------|-----------|
| korean-commit-message | O | O | PreToolUse (Bash) | command (Python) |
| korean-code-comments | O | O | PostToolUse (Write\|Edit\|MultiEdit) | command (Python) |
| ctx7-docs-lookup | O | O | PostToolUse (Bash) | command (Python) |
| activity-state | O | X | — | — |

## Directory Structure

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
│   │       ├── validate_commit.py
│   │       └── rules.md
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
      "description": "Korean conventional commit 메시지 규칙 적용 및 자동 검증 (Skill + Hook)",
      "source": "./plugins/korean-commit-message"
    },
    {
      "name": "korean-code-comments",
      "description": "코드 작성/수정 시 복잡한 로직에 한국어 주석 자동 리마인드 (Skill + Hook)",
      "source": "./plugins/korean-code-comments"
    },
    {
      "name": "ctx7-docs-lookup",
      "description": "반복 오류 시 ctx7로 공식 문서 참조 자동 감지 (Skill + Hook)",
      "source": "./plugins/ctx7-docs-lookup"
    },
    {
      "name": "activity-state",
      "description": "Next.js cacheComponents 환경에서 React Activity 상태 보존 버그 방지",
      "source": "./plugins/activity-state"
    }
  ]
}
```

### Plugin.json (각 플러그인)

```json
{
  "name": "<plugin-name>",
  "description": "<description>",
  "author": {
    "name": "brain1401"
  }
}
```

## Hook Designs

### Design Principle

Hook과 Skill은 독립적인 이중 안전장치로 동작한다:

- **Skill**: Claude가 작업을 시작할 때 로드 → 상세 규칙/패턴/예시 제공
- **Hook**: 특정 이벤트 발생 시 자동 실행 → 검증/리마인드 (Skill이 로드되지 않았을 때의 백업)

Hook의 systemMessage에는 `hooks/rules.md` 파일의 내용이 포함되어, 핵심 규칙과 예시가 전달된다.

### 1. korean-commit-message

**이벤트**: PreToolUse (matcher: `Bash`)

**`hooks/hooks.json`**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/validate_commit.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**`hooks/validate_commit.py`** 동작:
1. stdin에서 `tool_input.command` 파싱
2. `git commit` 명령이 아니면 `exit(0)` (통과)
3. 커밋 메시지 추출 (`-m` 플래그 파싱)
4. 검증 항목:
   - `<type>: <subject>` 포맷 확인
   - type이 허용 목록(feat/fix/docs/style/refactor/test/chore/perf/build/ci)에 포함되는지
   - subject 50자 이하
   - subject 첫 글자 대문자
   - subject 끝에 마침표 없음
5. 검증 실패 시: `rules.md` 읽어서 JSON 출력 후 `exit(2)`
   ```json
   {
     "hookSpecificOutput": { "permissionDecision": "deny" },
     "systemMessage": "<rules.md 내용>"
   }
   ```
6. 검증 성공 시: `exit(0)`

**`hooks/rules.md`**: SKILL.md의 핵심 규칙 축약본 (포맷, types 표, subject 규칙, 예시)

### 2. korean-code-comments

**이벤트**: PostToolUse (matcher: `Write|Edit|MultiEdit`)

**`hooks/hooks.json`**:
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
2. 편집된 파일이 코드 파일인지 확인 (확장자: `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.java`, `.go`, `.rs`, `.kt`, `.swift`, `.c`, `.cpp`, `.h`)
3. 코드 파일이 아니면 `exit(0)`
4. 세션별 상태 파일 (`/tmp/claude_comments_reminded_{session_id}`) 확인
5. 이미 리마인드했으면 `exit(0)`
6. 첫 코드 편집이면:
   - 상태 파일 생성
   - `rules.md` 읽어서 stderr로 출력
   - `exit(2)`

**`hooks/rules.md`**: 주석 스타일 규칙 + O/X 예시 (존댓말 금지, 콜론 금지, em dash 금지, 명사형 종결, 번호 형식)

### 3. ctx7-docs-lookup

**이벤트**: PostToolUse (matcher: `Bash`)

**`hooks/hooks.json`**:
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
2. `tool_result`에서 에러 감지 (exit code 비정상 또는 stderr에 에러 패턴)
3. 에러가 아니면 `exit(0)`
4. 세션별 상태 파일 (`/tmp/claude_error_count_{session_id}.json`)에 에러 카운트 기록
5. 카운트 < 2이면 `exit(0)`
6. 카운트 >= 2이면:
   - `rules.md` 읽어서 stderr로 출력
   - 카운터 리셋 (같은 세션에서 다시 반복되면 재트리거)
   - `exit(2)`

**`hooks/rules.md`**: ctx7 사용 리마인드 + 핵심 쿼리 전략 요약

## Migration Plan

### 파일 이동 (기존 → 신규)

| 기존 경로 | 신규 경로 |
|-----------|-----------|
| `skills/korean-commit-message/SKILL.md` | `plugins/korean-commit-message/skills/korean-commit-message/SKILL.md` |
| `skills/korean-code-comments/SKILL.md` | `plugins/korean-code-comments/skills/korean-code-comments/SKILL.md` |
| `skills/ctx7-docs-lookup/SKILL.md` | `plugins/ctx7-docs-lookup/skills/ctx7-docs-lookup/SKILL.md` |
| `skills/activity-state/SKILL.md` | `plugins/activity-state/skills/activity-state/SKILL.md` |
| `skills/activity-state/references/activity-behavior.md` | `plugins/activity-state/skills/activity-state/references/activity-behavior.md` |

### 삭제 대상

- `skills/` 디렉토리 (이동 후)

### 신규 생성

- `.claude-plugin/marketplace.json`
- 각 플러그인의 `.claude-plugin/plugin.json`
- 각 플러그인의 `hooks/hooks.json` (3개)
- 각 플러그인의 `hooks/*.py` (3개)
- 각 플러그인의 `hooks/rules.md` (3개)
- `README.md` (마켓플레이스 설치 가이드로 전면 개정)

### Git 작업

- 기존 원격 레포 삭제 완료 (사용자 확인)
- 새 원격 레포 `brain1401/claude-plugins` 생성
- remote origin 변경

## Installation (사용자 측)

```bash
# 마켓플레이스 등록
/plugin marketplace add brain1401/claude-plugins

# 개별 플러그인 설치
/plugin install korean-commit-message@brain1401
/plugin install korean-code-comments@brain1401
/plugin install ctx7-docs-lookup@brain1401
/plugin install activity-state@brain1401
```

## Testing

각 플러그인 로컬 테스트:
```bash
cc --plugin-dir plugins/korean-commit-message
```

Hook 스크립트 단위 테스트:
```bash
echo '{"tool_input": {"command": "git commit -m \"feat: test\""}, "session_id": "test"}' | \
  python3 plugins/korean-commit-message/hooks/validate_commit.py
echo "Exit code: $?"
```
