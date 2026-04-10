---
name: git-workflow
description: Use when committing, pushing, branching, or working with PRs. Enforces the feature branch + PR + Squash merge policy for behavioral changes (product code, tests, dependencies) while allowing direct `main` commits for docs, tooling, and behavior-preserving refactors. Invoke BEFORE any `git commit`, `git push`, `gh pr create`, or `gh pr merge` — the rules around direct `main` commits are non-obvious and the wrong merge mode (regular/rebase instead of squash) corrupts `main` history. Also covers intra-branch commit hygiene, branch patterns (single/stacked/parallel), rebase conflict resolution, draft PRs, PR sizing, PR message format, and how to revert. For brainstorming/planning workflows that produce spec/plan documents, also see the `spec-first-workflow` skill.
---

# Git Workflow

This skill enforces a **feature branch + PR + Squash merge** flow for behavioral changes (product code, tests, dependencies). Documentation, tooling, and small behavior-preserving refactors can land directly on `main`. This skill walks through the right steps and prevents the most common mistake: merging without squash.

## When to use a feature branch (behavioral changes)

Open a feature branch + PR for any change that could affect product behavior:

- Production code (application source, library source, except small behavior-preserving refactors — see below)
- Tests (additions, modifications, removals)
- Dependencies (`package.json`, `pnpm-lock.yaml`, `pyproject.toml`)
- Build/CI/turbo config (`turbo.json`, CI workflows)
- Schema changes or migrations
- Environment templates (`.env.example`) when the change affects runtime behavior
- Anything you're not confident is safe for direct commit

> **For brainstorming/planning workflows**: When `superpowers:brainstorming` or `superpowers:writing-plans` produce spec/plan documents, follow the `spec-first-workflow` skill. Those commits land on the feature branch but the PR only opens after implementation is ready.

When in doubt about production code, branch. The cost of opening a PR is small; the cost of a broken `main` is large.

## When direct commit to `main` is allowed

Direct commits are fine for **non-behavioral** changes where a PR would add ceremony without adding safety. These are normal cases, not rare exceptions — use your judgment, but don't default to branching just because "policy".

Direct commits are *allowed* here, not *required*. You can always open a PR if you want independent review, especially for non-trivial skill rewrites or rule changes.

### Documentation

- `docs/` hierarchy, `README.md`, `CLAUDE.md`
- Rule files under `.claude/rules/`
- Code comments (adding, editing, removing)
- Typo fixes, formatting, rewrites that don't change meaning

### Tooling and project config

- Skills, commands, agents, hooks under `.agents/` and `.claude/`
- `.gitignore`, editor config (`.editorconfig`, `.vscode/`, etc.)
- Prettier/ESLint/Ruff config that doesn't shift semantics

### Small behavior-preserving refactors

Code changes that clearly don't change runtime behavior:

- Renaming local variables, functions, or files (with call-site updates)
- Extracting a constant, inlining a one-liner, moving a helper
- Reordering imports, fixing formatting
- Removing provably-dead code (variables/functions never referenced)

If you have to argue the case for "it really doesn't change behavior", that's your signal to open a PR instead. The benefit of a PR is independent review; if the change is subtle enough that review would add value, branch.

### Hotfix for broken CI

When `main` is red and a full PR flow isn't practical. Include an explanatory commit message and open a follow-up PR with context as soon as possible.

### Bundling still matters

Even within the allowed categories, keep commits atomic — one logical change per commit, same as within a feature branch. "Fix docs typo AND extract constant AND update skill" is three commits, not one mega-commit.

## Why this matters

- **`main` history stays clean**: 1 PR = 1 squash commit on `main`. `git log --oneline` becomes a useful summary instead of a wall of WIP commits.
- **Individual commits are not lost**: the GitHub PR page (Commits tab) preserves them forever, even after the branch is deleted.
- **PR-level revert is trivial**: `gh pr revert <num>` or `git revert <squash-hash>`. One command to undo a logical change.
- **Trade-off**: the unit of revert on `main` becomes "1 PR". This is exactly why PRs must stay small — one logical change per PR.

## Standard flow

```bash
# 1. Start fresh from main
git checkout main && git pull

# 2. Branch with intent prefix
git checkout -b feat/short-description

# 3. Commit with meaningful messages (see "Commits within a branch" below)
git add <files>
git commit -m "..."   # ← if a commit message skill is configured, invoke it

# 4. Run tests — unit AND E2E (see "Testing before PR" below)
# Run the project's unit test and E2E test commands

# 5. Push and open PR (see "PR message format" below for the body structure)
git push -u origin feat/short-description
gh pr create --title "feat: ..." --body "..."

# 6. After CI passes, squash merge AND delete the branch
gh pr merge --squash --delete-branch

# 7. Sync main
git checkout main && git pull
```

**Note on commit messages:** If a commit message skill is configured for this project (e.g., via plugin or `.claude/` rules), invoke it when running `git commit`.

## Testing before PR

Both unit tests and E2E tests must be run before creating a PR. Results go in the PR's Testing section. In-process tests (e.g., `app.request()`, `TestClient`) count as unit tests — they do not substitute for E2E tests.

Run the project's configured unit and E2E test commands. If the project defines E2E test methods per scope (e.g., frontend Playwright tests, backend real HTTP verification), follow those. Check `.claude/rules/testing.md` or equivalent project documentation for the exact commands.

Non-behavioral changes (docs, rule files, skills) are exempt from E2E testing.

## Commits within a branch

Under squash merge, the branch collapses into one commit on `main`, so intra-branch history isn't what lands in `main`'s log. Two habits are still worth following; the rest is optional polish.

### Required

**Meaningful commit messages.** `WIP`, `fix typo`, `oops` titles leak into both the PR Commits tab and the squash commit's body (GitHub copies commit titles as bullets by default). Each commit message should describe what the commit does. If a commit message skill is configured, invoke it.

**Clean up WIP / fixup commits before pushing.** Fold them into related commits with `git rebase -i`:

```bash
git rebase -i main          # squash fixups, reword sloppy messages
git push --force-with-lease
```

`--force-with-lease` is safe here since the branch is yours and the PR isn't merged. Avoid plain `--force` since it can clobber concurrent pushes.

### Recommended (optional polish)

Reordering commits into a "learning sequence", splitting one commit into smaller atomic units, or using `fixup!` to edit earlier commits all make the PR Commits tab a more useful review tool and make retroactive branch splitting easier.

But under squash merge, the final commit on `main` is identical either way. Invest this effort when the PR is genuinely educational (tricky refactor, non-obvious algorithm) or when you anticipate needing to split the branch into stacked PRs. For straightforward work, don't bother — the rebase gymnastics rarely pay off.

## Branch naming

Prefix by intent. Use kebab-case for the description:

- `feat/` — new feature (`feat/passkey-login`)
- `fix/` — bug fix (`fix/session-expiry-race`)
- `chore/` — maintenance, deps, config (`chore/bump-vitest`)
- `refactor/` — internal restructuring with no behavior change (`refactor/extract-llm-client`)
- `docs/` — documentation only (`docs/api-routing-section`)
- `test/` — test-only changes (`test/auth-edge-cases`)

## Keep PRs small

The single most important rule: **one logical change per PR**.

Rule of thumb: if you can't describe the PR in a single sentence without using "and", it's too big — split it.

Why this matters: revert granularity on `main` is "1 PR". A PR that bundles "auth refactor + new login UI + DB migration" cannot be partially reverted. Split such PRs into 3 separate PRs that can be reverted independently.

## Branch patterns (split big work into multiple branches)

Most non-trivial work is too big for one PR. Pick a pattern up-front based on whether the pieces depend on each other.

### 1. Single branch (small work)

One branch off `main`, one PR, merge, done. Use when the change is small enough that splitting would be artificial. The "Standard flow" above assumes this pattern.

```text
main ──●────────────●         (squash merge)
        \          /
         feat/X ──●──●──●
```

### 2. Stacked branches — vertical (most common)

When work B depends on work A: branch B off branch A (not off `main`), open both PRs, get A merged first, then rebase B onto `main`.

```text
main ──●─────────────── ●          (squash merge of A)
        \                \
   feat/A ──●──●──●        \
                  \          \
             feat/B ──●──●──● ── rebase onto new main ── (squash merge of B)
```

```bash
# A branches from main
git checkout main && git pull
git checkout -b feat/A
# ... work on A + create PR ...

# B branches from A (not from main)
git checkout feat/A
git checkout -b feat/B
# ... work on B + create PR. In the PR body, mark "Stacked on #<A's PR number>" ...

# After A is merged, rebase B onto the new main
git checkout feat/B
git fetch origin
git rebase origin/main      # A's squash commit is already on main, so this usually applies cleanly
git push --force-with-lease
```

**Critical**: A must be in a stable shape before stacking B on top of it. Design done, public interface settled. Otherwise every change to A forces a rebase of B and pollutes B's commit history with merge noise. **If you can't keep A stable, don't stack** — finish A, merge it, then start B from the new `main`.

This is the practical meaning of "plan work units up-front": before starting, read the spec, decide where the natural seams are, and branch along those seams.

### 3. Parallel branches — horizontal

Multiple independent branches off the same base. Use only when the changes truly don't touch each other. Rare in practice — most "independent" work turns out to share a file or two.

```text
main ──●─────────
        ├── feat/X ──●──●
        ├── feat/Y ──●──●──●
        └── feat/Z ──●
```

When the base branch changes, **rebase** each parallel branch onto the new base (not merge). Under squash merge, rebase usually applies cleanly.

### Resolving rebase conflicts

Rebasing onto an updated base can produce conflicts. This is most common with stacked branches after the parent has been squash-merged: `main` now has a single squash commit combining several originals, but your branch was built on the pre-squash versions.

**Basic flow** for a rebase conflict:

```bash
git rebase origin/main
# ...conflict appears...
# Edit the conflicting files, keeping the side that should win
git add <resolved-files>
git rebase --continue
# Repeat if more conflicts appear during subsequent commits
git push --force-with-lease
```

**Stacked branch specific case**: after A is squash-merged, B's original branch point is no longer in `main`'s history. `git rebase origin/main` replays B's commits on top of A's squash commit. Commits that were part of A's work (carried along in B's history) usually drop out cleanly — git detects they're already applied — but sometimes git tries to reapply a change that the squash commit already contains and flags it as a conflict. In that case, accept the squash commit's version (`git checkout --theirs <file>`, or manually keep the content from `main`) and continue.

**When to abort**: if you're accepting "theirs" for nearly every file, or conflicts pile up beyond a handful, something went wrong at the branching step — most likely B was stacked before A was stable. Run `git rebase --abort` to return to the pre-rebase state, then either re-branch from fresh `main` and cherry-pick B's meaningful commits, or start B over against the new `main`. Don't grind through 20 hand-resolved conflicts when a clean restart is cheaper.

### Tip: write everything in one branch first, split later

If the boundaries aren't clear up-front, do all the work on one branch first. If it later turns out the branch should have been multiple PRs, you can `git checkout -b` at intermediate commits and split into stacked branches retroactively.

Retroactive splitting is cleanest when commits happen to be reasonably atomic — so if you anticipate a possible split, keep commit units small as you go. Otherwise don't stress about it; worst case you resort to ad-hoc `git reset` + `git add -p` to carve out the pieces.

## PR message format

The PR title becomes the squash commit title on `main` after merge, so it must follow the project's commit message convention (e.g., conventional commits, ≤70 chars, no trailing period). If a commit message skill is configured, follow its format:

- `feat: 패스키 로그인 추가`
- `fix(api): 세션 만료 경합 조건 해결`
- `chore(deps): vitest 3.0으로 업데이트`

For the PR body, use the **What / Why / How / Testing** structure. Korean by default; English is fine for technical terms and code identifiers.

### Standard body template

```markdown
## What
무엇이 바뀌었는지 (1~3줄)

## Why
왜 이 변경이 필요했는지 (배경, 동기, 제약)

## How
어떻게 접근했는지 (구현 전략, 트레이드오프). 자명하면 생략

## Testing
Separate unit test and E2E test results. E2E tests are mandatory.

### Unit tests
- [ ] `pnpm test` results (Vitest / pytest, include test count)

### E2E tests
- [ ] E2E verification for the changed scope
  - Frontend: Playwright (`pnpm test:e2e`)
  - Backend: start server + verify with real HTTP requests (`pnpm dev` → `curl` / Playwright)
  - List test scenarios and pass/fail status

Closes #123
```

### Korean body conventions

When the PR body is written in Korean, in-text content (paragraph body, list item bodies) must follow these tone rules. Section headings (`## What`, `## Why`, `## How`, `## Testing`) and conventional commit prefixes (`docs(skill):`) are exempt because they are format markers, not content. If a code comment convention skill is configured, its tone rules also apply here.

- **명사형 종결**: noun-phrase endings only ("추가", "수정", "검증 통과"). No `-합니다`/`-했습니다` formal endings, no `-함`/`-했음` colloquial endings.
- **No colons (`:`) in in-text content**: use parentheses `()`, or restructure with Korean particles (e.g., "원칙: X" → "원칙은 X"). Avoid blunt period replacement, which often leaves awkward sentence fragments.
- **No em dash (U+2014) in in-text content**: use parentheses, commas, periods, or restructure.
- **Multi-step explanations**: use `1. 2. 3.` numbering, not `[1] [2]`.

```text
✓ 핵심 원칙은 brainstorming 산출물(spec, plan)이 그 자체로 PR의 단위가 아님
✗ 핵심 원칙: brainstorming 산출물(spec, plan)이 그 자체로 PR의 단위가 아님

✓ 다음 세션에서 행동 관찰 (사후 검증, spec §6 시나리오 1~4)
✗ 다음 세션에서 행동 관찰 — 사후 검증, spec §6 시나리오 1~4

✓ 1. feature branch 생성  2. spec commit  3. 구현 commit
✗ [1] feature branch 생성  [2] spec commit  [3] 구현 commit
```

These rules apply to in-text Korean content only. English body sections (technical terms, identifiers, code blocks) follow standard English conventions.

### Write for readers who weren't in the room

PR titles and bodies are read by reviewers and future contributors with no context from the conversation that produced the change. Internal labels from brainstorming or design discussions (e.g., "Option A/B/C", "Approach 2", "Strategy 3") are meaningless to anyone who wasn't part of that conversation. Always expand internal shorthand into its actual meaning.

```text
✗ DB 접근 전략 Option C 확정
✓ LLM 서버는 PostgreSQL에 직접 접근하지 않고 Hono API를 경유

✗ 접근법 1(Strict Feature-Based)로 진행
✓ 피처 기반 구조로 전환 (도메인별 router/service/schemas 분리)
```

This applies to both the PR title and body. Even if the design spec (`docs/superpowers/specs/`) uses internal labels, the PR must stand on its own — a reader should understand every statement without consulting any other document.

### `--fill` vs manual

- **`--fill` is fine when**: single-commit PR AND the commit message is self-explanatory (e.g., `chore: vitest 3.0으로 업데이트`). The commit message becomes the PR body verbatim, so this is the fastest path for trivial PRs.
- **Write manually when**: multi-commit PR, non-obvious tradeoffs, UI changes, or any change that needs context the commit messages alone can't carry. Most non-trivial PRs fall here.

### Creating a PR with the template

```bash
gh pr create --title "feat: 패스키 로그인 추가" --body "$(cat <<'EOF'
## What
- 로그인 페이지에 WebAuthn 패스키 옵션 추가
- Better Auth의 passkey 플러그인 통합

## Why
비밀번호 없는 로그인 요구가 늘고 있음. 카카오/네이버 OAuth만으로는 데스크톱에서 마찰이 큼.

## How
1. Better Auth `passkey` 플러그인 활성화
2. `apps/web/src/app/(auth)/login/passkey-button.tsx` 추가
3. 등록 플로우는 후속 PR로 분리

## Testing
### Unit tests
- [x] Vitest: passkey auth handler tests (3 files, 12 tests passed)

### E2E tests
- [x] Playwright: login → passkey registration → re-login scenario passed
- [x] Manual: verified real passkey registration in Chrome/Safari

Closes #45
EOF
)"
```

### Optional sections

Add only when relevant. Don't add empty sections:

- `## Screenshots` — for UI changes (drag-and-drop images, or `![description](url)`)
- `## Breaking changes` — when API or schema changes break compatibility. Include a migration guide
- `## Background` — when Why alone isn't enough for deep context (prior attempts, alternatives considered, external constraints)

### Why this format

- **What** alone is self-evident from the diff. **Why** is what reviewers actually need.
- Lead with What (one-line summary) so reviewers can decide whether to dig in. Then Why for motivation, then How for implementation discussion.
- Testing as a checklist (`- [ ]`) is GitHub-clickable and shows the author actually thought about verification rather than leaving it to the reviewer.
- `Closes #N` auto-closes the issue on merge. Use `Refs #N` if related but not closing.

### Draft PRs

A draft PR is a PR marked "not ready for review yet" — it appears on GitHub with a grey badge instead of green, and reviewers know not to spend time on it yet. Create one with `gh pr create --draft ...` and flip it to ready with `gh pr ready <number>` once the work is actually reviewable.

**Use draft when:**

- **Early CI signal** — you want CI running against WIP without pulling reviewers in yet
- **Soliciting feedback on direction** — the approach itself is uncertain and you want input on the overall shape before polishing the details
- **Stacked PR whose parent hasn't merged yet** — keep the child as draft until its parent lands, so reviewers aren't confused about which PR to look at first
- **Long-running work across sessions** — the branch will sit for a while (blocked on something, or intentionally held) and you want it visible so the work doesn't go stale in a private branch

**Don't use draft as a way to delay review indefinitely.** A draft sitting for more than a few days without movement is a signal something's wrong — either the work is stuck (raise it) or the branch is dead (close it). Draft is a lifecycle marker, not a shelf.

When flipping to ready, double-check the PR body still matches reality — draft PRs often get opened with placeholder descriptions.

## Merge mode (CRITICAL)

**Always Squash and merge.** Never use:

- Regular merge — creates a merge commit AND brings all branch commits onto `main`
- Rebase merge — brings all branch commits onto `main` flat
- **Squash merge** — collapses the branch into a single commit on `main` ← always use this

The `gh pr merge --squash --delete-branch` form does the right thing AND cleans up the branch in one command.

If GitHub blocks squash merge, check repo settings:
Settings → General → Pull Requests → enable "Allow squash merging", disable the others.

## Recovering / reverting

```bash
# Revert a whole PR (the squash commit)
gh pr revert <pr-number>
# or, locally:
git revert <squash-commit-hash>

# Inspect an individual commit from a merged PR
gh pr view <pr-number> --json commits                     # list commits
git fetch origin pull/<pr-number>/head:pr-<pr-number>     # pull branch back
git show <individual-commit-hash>
```

The squash commit message also includes the original commit titles (GitHub's default), so `git log` on `main` already shows what was in each PR without any extra steps.

## Common mistakes

- **Direct commit to `main` for behavioral changes** — The direct-commit path is for docs, tooling, and behavior-preserving refactors. Using it to skip review on product code, tests, or dependencies defeats the safety the PR flow provides.
- **Bundling unrelated changes in one PR** — Split. Future-you will thank present-you when reverting.
- **Forgetting `--delete-branch`** — Always use `gh pr merge --squash --delete-branch`. Or run `git push origin --delete feat/xxx` after.
- **Using regular merge by accident** — Always pass `--squash`. Even better: configure the repo to only allow squash merging in repo settings.
- **Long-lived branches** — Merge fast. Long branches accumulate conflicts and lose context. If you need early visibility without pulling reviewers in, use a draft PR (see "Draft PRs" subsection for criteria).
- **Pushing WIP/fixup commits as-is** — Clean them up with `git rebase -i` before pushing. They show up in both the PR Commits tab and the squash commit's body.
- **Starting a stacked branch before the base is stable** — If A is still in flux, building B on top of it leads to rebase hell. Stabilize A first, or merge it before starting B.
