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
