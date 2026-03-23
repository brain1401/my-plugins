# skill.md

AI 코딩 에이전트용 스킬 모음

## Skills

| Name | Description | Install |
| --- | --- | --- |
| [korean-code-comments](skills/korean-code-comments/SKILL.md) | 코드 작성/수정 시 복잡한 로직에 한국어 주석 작성 | `npx skills add brain1401/skill.md --skill korean-code-comments` |
| [korean-commit-message](skills/korean-commit-message/SKILL.md) | Korean conventional commit 메시지 규칙 적용 | `npx skills add brain1401/skill.md --skill korean-commit-message` |
| [activity-state](skills/activity-state/SKILL.md) | Next.js `cacheComponents` 환경에서 React Activity 상태 보존으로 인한 버그 방지 | `npx skills add brain1401/skill.md --skill activity-state` |
| [ctx7-docs-lookup](skills/ctx7-docs-lookup/SKILL.md) | 반복 오류 발생 시 또는 계획 수립 시 확신 부족할 때 ctx7으로 공식 문서 참조 강제 | `npx skills add brain1401/skill.md --skill ctx7-docs-lookup` |

## Install

```bash
# 전체 스킬 설치
npx skills add brain1401/skill.md

# 스킬 목록 확인
npx skills add brain1401/skill.md --list

# 특정 스킬만 설치
npx skills add brain1401/skill.md --skill korean-code-comments

# 특정 에이전트에만 설치
npx skills add brain1401/skill.md -a claude-code

# 글로벌 설치
npx skills add brain1401/skill.md --global
```
