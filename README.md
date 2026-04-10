# claude-plugins

brain1401의 Claude Code 플러그인 마켓플레이스

## Plugins

| Plugin | Description | Hook |
| --- | --- | --- |
| [korean-commit-message](plugins/korean-commit-message/) | Korean conventional commit 메시지 규칙 적용 및 자동 검증 | PreToolUse (Bash) |
| [korean-code-comments](plugins/korean-code-comments/) | 코드 작성/수정 시 복잡한 로직에 한국어 주석 자동 작성 | PostToolUse (Write/Edit) |
| [activity-state](plugins/activity-state/) | Next.js cacheComponents 환경에서 React Activity 상태 버그 방지 | - |
| [claude-docs-integrity](plugins/claude-docs-integrity/) | CLAUDE.md와 .claude/rules/ 간 정합성, 중복성, 경로 유효성, 교차 참조 검증 및 수정 | - |

## Install

```bash
# 마켓플레이스 등록
/plugin marketplace add brain1401/claude-plugins

# 개별 플러그인 설치
/plugin install korean-commit-message@claude-plugins
/plugin install korean-code-comments@claude-plugins
/plugin install activity-state@claude-plugins
/plugin install claude-docs-integrity@claude-plugins
```

## Architecture

### Skill + Hook 하이브리드 (korean-commit-message, korean-code-comments, activity-state)

- **Skill**: Claude가 작업 시작 시 로드. 상세 규칙, 패턴, 예시를 포함한 완전한 가이드 제공
- **Hook**: 특정 이벤트 발생 시 자동 실행. 검증 또는 핵심 규칙 리마인드

둘은 독립적인 이중 안전장치로, Skill이 invoke되지 않아도 Hook이 핵심 규칙을 보장합니다.

### Multi-Agent Pipeline (claude-docs-integrity)

3개 에이전트 파이프라인 (Planner → Generator → Evaluator) + 경량 자동 트리거:

- **Planner**: 프로젝트 문서 발견 + 고수준 감사 계획 (WHAT만 정의, HOW 미지정)
- **Generator**: Sprint Contract 작성 + 4개 검증 축 병렬 서브에이전트 실행
- **Evaluator**: Sprint Contract 대비 독립 검증 + 스팟체크 + 최종 보고서
- **Integrity-check**: CLAUDE.md/rules 수정 후 자동 퀵 체크 (haiku)

파일 기반 소통 (`.claude-docs-integrity/` 작업 디렉토리), 재작업 루프 (최대 1회).
