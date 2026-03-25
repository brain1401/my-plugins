---
name: korean-commit-message
description: This skill should be used when creating git commits, writing commit messages, or when the user asks to "commit", "커밋", "커밋 메시지 작성", or any commit-related workflow. Enforces Korean conventional commit message format with specific type prefixes (feat, fix, docs, etc.), subject line rules, and body/footer conventions. Applies to all commit message composition tasks.
---

# Korean Conventional Commit Message Guide

When creating a git commit, follow this format strictly. This ensures consistent, readable git history across the project.

## Commit Message Structure

```
<type>: <subject>

<body>

<footer>
```

## Types

| Type | Purpose |
|------|---------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation changes only |
| style | Formatting, semicolons, etc. (no logic change) |
| refactor | Code restructuring without behavior change |
| test | Adding or modifying tests |
| chore | Build process, tooling, dependency updates |
| perf | Performance improvement |
| build | Build system or external dependency changes |
| ci | CI configuration changes |

## Subject Rules

- 50 characters or fewer
- No trailing period or punctuation
- **Korean subject preferred.** Use the noun-phrase pattern ("명사 + 동사"). Do not use formal endings (-합니다, -했습니다) or colloquial endings (-함, -했음).
- When writing in English: start with an uppercase letter, use imperative mood (e.g. "Add feature", not "Added feature")

**Good examples:**
```
feat: 사용자 로그인 기능 추가
fix: 잘못된 세션 만료 처리 수정
docs: Update API documentation
```

**Bad examples:**
```
feat: added user login feature.   ← English: lowercase, trailing period, past tense
feat: 사용자 로그인 기능을 추가했습니다  ← Korean: formal ending (-했습니다)
feat: 사용자 로그인 기능 추가함        ← Korean: colloquial ending (-함)
```

## Body Rules

The body is optional. Include it when the subject alone does not convey enough context.

- Separate from the subject with a blank line
- Wrap each line at 72 characters
- Explain **what** changed and **why**, not **how** (the code shows how)
- Write body text in Korean. English is acceptable for technical terms or when the audience is international

**Examples:**
```
feat: 사용자 로그인 기능 추가

- 사용자 인증을 위해 JWT 사용
- 로그인 API 엔드포인트 추가
- 로그인 페이지 UI 구현

Closes #45
```

```
fix: 로그인 오류 수정

- 잘못된 비밀번호 입력 시 오류 메시지 표시
- 세션 만료 시 자동 로그아웃 기능 추가
```

## Footer Rules

The footer is optional. Use it for:

- **Breaking changes**: `BREAKING CHANGE: description`
- **Issue references**: `Closes #123`, `Fixes #456`

## When Composing the Commit Message

1. Look at the staged changes (`git diff --cached`) to understand what was modified
2. Choose the most appropriate type based on the primary intent of the changes
3. Write a clear subject summarizing the change in imperative mood
4. Add a body only if the subject is not self-explanatory
5. Add a footer if there are related issues or breaking changes
