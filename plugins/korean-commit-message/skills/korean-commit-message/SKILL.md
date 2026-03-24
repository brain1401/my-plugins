---
name: korean-commit-message
description: Enforces Korean conventional commit message format when creating git commits. Use this skill whenever committing code, writing commit messages, or when the user asks to commit, push, or create a PR. Also applies when the user invokes /commit or any commit-related workflow. If a git commit is about to happen, this skill MUST be consulted.
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
- Start with an uppercase letter
- No trailing period
- Use imperative mood (e.g. "Add feature", not "Added feature")

**Example 1:**
```
feat: Add user login feature
```

**Example 2 (wrong):**
```
feat: added user login feature.
```
The subject starts lowercase and has a trailing period — both violate the rules.

## Body Rules

The body is optional. Include it when the subject alone does not convey enough context.

- Separate from the subject with a blank line
- Wrap each line at 72 characters
- Explain **what** changed and **why**, not **how** (the code shows how)
- Write in Korean when explaining domain context; English is also acceptable

**Example:**
```
feat: Add user login feature

- JWT authentication for user sessions
- Login API endpoint added
- Login page UI implemented

Closes #45
```

## Footer Rules

The footer is optional. Use it for:

- **Breaking changes**: `BREAKING CHANGE: description`
- **Issue references**: `Closes #123`, `Fixes #456`

## Full Examples

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

```
docs: Update API documentation
```

```
refactor: Extract authentication logic into service layer
```

## When Composing the Commit Message

1. Look at the staged changes (`git diff --cached`) to understand what was modified
2. Choose the most appropriate type based on the primary intent of the changes
3. Write a clear subject summarizing the change in imperative mood
4. Add a body only if the subject is not self-explanatory
5. Add a footer if there are related issues or breaking changes
