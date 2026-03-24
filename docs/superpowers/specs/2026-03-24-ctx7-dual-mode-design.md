# ctx7-docs-lookup Dual Mode Support Design

## Overview

ctx7-docs-lookup 플러그인이 MCP와 CLI(skill) 두 가지 방식의 context7 접근을 자동으로 감지하고 적절한 방식을 사용하도록 업데이트한다.

## Problem

현재 플러그인은 MCP 도구(`mcp__context7__*`)만을 명시적으로 안내한다. context7이 CLI/skill(`find-docs`) 형태로도 제공되지만, MCP가 없는 환경에서는 플러그인이 사실상 무용지물이다.

## Goals

1. MCP와 CLI(skill) 두 가지 context7 접근 방식 모두 지원
2. 세션 시작 시 사용 가능한 방식을 자동 감지하여 환경 변수에 저장
3. SKILL.md가 감지 결과에 따라 해당 방식만 안내하여 컨텍스트 비용 절약
4. 감지 실패 시 graceful fallback 제공

## Design

### 1. SessionStart Detection Hook

**파일:** `hooks/scripts/detect_ctx7_mode.sh`

세션 시작 시 실행되는 bash 스크립트. 아래 위치에서 `context7` MCP 서버 설정을 검색:

| Priority | Location | Scope |
|----------|----------|-------|
| 1 | `$CLAUDE_PROJECT_DIR/.mcp.json` | Project |
| 2 | `$CLAUDE_PROJECT_DIR/.claude/settings.json` | Project |
| 3 | `$CLAUDE_PROJECT_DIR/.claude/settings.local.json` | Project |
| 4 | `~/.claude/.mcp.json` | Global |
| 5 | `~/.claude/settings.json` | Global |
| 6 | `~/.claude/settings.local.json` | Global |

**감지 로직:**

- `jq`를 사용하여 각 파일의 `mcpServers` 객체 키를 파싱하고, 키 이름에 `context7` 또는 `ctx7`이 포함되어 있는지 확인 (대소문자 무시)
- 발견되면 `CTX7_MODE=mcp` → `$CLAUDE_ENV_FILE`에 기록, 즉시 종료
- 모든 파일 검색 후 미발견 시 `CTX7_MODE=skill` 기록
- `jq` 미설치, 파일 파싱 실패 등 예외 시 `CTX7_MODE=unknown` 기록
- `$CLAUDE_ENV_FILE`이 미설정된 경우 감지를 건너뛰고 즉시 종료 (exit 0)
- 항상 exit 0 (세션 시작을 차단하지 않음)

**환경 변수 스코프:**

- `$CLAUDE_ENV_FILE`은 세션 스코프이며, 각 세션 시작 시 새로 작성된다. 이전 세션의 값이 다음 세션에 잔존하지 않는다.

### 2. hooks.json Update

기존 `PostToolUse` hook에 `SessionStart` hook 추가:

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

### 3. SKILL.md "How to Use context7" Section Update

기존의 테이블 기반 설명을 `$CTX7_MODE` 조건 분기로 교체:

- **`CTX7_MODE=mcp`**: MCP 도구 직접 사용 (`mcp__context7__resolve-library-id`, `mcp__context7__query-docs`)
- **`CTX7_MODE=skill`**: `find-docs` skill 호출
- **`CTX7_MODE=unknown` 또는 미설정**: MCP 시도 → 실패 시 skill fallback → 둘 다 실패 시 사용자에게 설치 안내

**`unknown` fallback 실패 판단 기준:**

- MCP 실패: 도구가 존재하지 않는 경우 (tool not found / unknown tool 에러)
- Skill 실패: `find-docs` skill이 사용 가능한 skill 목록에 없는 경우
- 두 방식 모두 실패 시, 사용자에게 "context7 MCP 서버를 .mcp.json에 추가하거나, find-docs skill이 포함된 플러그인을 설치하세요"라고 안내

나머지 섹션(Why, When NOT to Use, Trigger Conditions, Important Notes, References)은 변경 없음.

**`$CTX7_MODE`와 rules.md 연동:**

`rules.md`는 `detect_repeated_errors.py`에 의해 `systemMessage`로 주입된다. 이 시점에서 `$CTX7_MODE`는 이미 `$CLAUDE_ENV_FILE`을 통해 세션 환경 변수로 설정되어 있으므로, LLM이 `rules.md`의 "$CTX7_MODE에 따라 행동하라"는 지시를 해석할 수 있다.

### 4. rules.md Mode Neutralization

현재 하드코딩된 MCP 도구명(`mcp__context7__resolve-library-id → mcp__context7__query-docs`)을 제거하고 모드 중립적 표현으로 교체:

```
Query official docs via context7 (follow the method specified by $CTX7_MODE in the ctx7-docs-lookup skill)
```

Query Strategy, Do NOT 섹션은 변경 없음.

## File Changes Summary

| File | Action |
|------|--------|
| `hooks/scripts/detect_ctx7_mode.sh` | **New** — SessionStart 감지 스크립트 |
| `hooks/hooks.json` | **Edit** — SessionStart hook 추가 |
| `skills/ctx7-docs-lookup/SKILL.md` | **Edit** — How to Use 섹션 조건 분기로 교체 |
| `hooks/rules.md` | **Edit** — 모드 중립적 표현으로 변경 |

## Non-Goals

- context7 설치 자동화
- 세션 중간에 모드 전환 (환경 변수는 세션 시작 시 고정, `$CLAUDE_ENV_FILE`은 세션 스코프)
- `find-docs` skill 존재 여부의 사전 감지 (bash에서 skill 목록 접근 불가, `unknown` fallback이 커버)
