# Commit Format Reference

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
