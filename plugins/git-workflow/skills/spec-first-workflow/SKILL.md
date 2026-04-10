---
name: spec-first-workflow
description: Use when running superpowers:brainstorming, superpowers:writing-plans, or committing spec/plan documents produced by those skills. Covers why the spec + plan + implementation share a single feature branch (not standalone PRs), when to defer push/PR until implementation is ready, how to handle reference materials the user adds during brainstorming, and how to discard a brainstorming branch that doesn't pan out. Invoke BEFORE the first `git commit` of any brainstorming output — the "should this be its own PR?" question is non-obvious and getting it wrong creates PR ceremony for non-feature work.
---

# Spec-First Workflow

When work begins from a brainstorming or planning skill (`superpowers:brainstorming`, `superpowers:writing-plans`), design/spec/plan documents are produced *before* any implementation code. Those documents belong in git, but they are **not standalone PRs** — they are part of the feature they describe.

The right pattern: **create the feature branch early (during brainstorming), commit the spec/plan there, defer push and PR until implementation is ready**.

```text
main
  └── refactor/some-feature (local only during brainstorming)
        ├── Commit 1: docs: <feature> 설계서 추가          ← spec from brainstorming
        ├── Commit 2: docs: <feature> 구현 계획 추가        ← plan from writing-plans
        ├── Commit 3..N: feat/refactor/test/...           ← actual implementation
        └── (구현 완료 시 push + PR 오픈, squash merge)
```

## Why this pattern

- **PR remains feature-unit** — one logical change per PR, where the "change" is the feature including its design rationale. Spec + plan + implementation all land as a single squash commit on `main`.
- **Spec is preserved in git** — satisfies the brainstorming skill's "commit the design document" requirement without creating PR ceremony for a non-feature.
- **Reviewers see context inline** — the PR's Commits tab walks reviewers from "why this exists" (spec) → "how it will be done" (plan) → "the actual diff" (implementation).
- **Branch is reversible** — if the user abandons the brainstorming halfway, `git branch -D <branch>` discards all commits with no main pollution.

## Workflow

```bash
# 1. Brainstorming starts — create the feature branch immediately
git checkout main && git pull
git checkout -b refactor/some-feature

# 2. brainstorming skill writes the spec. Commit it locally (no push)
git add docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
git commit -m "..."   # ← if a commit message skill is configured, invoke it

# 3. writing-plans skill writes the plan. Commit locally
git add docs/superpowers/plans/YYYY-MM-DD-<topic>-plan.md
git commit -m "..."

# 4. Implementation begins on the same branch (see git-workflow skill for intra-branch commit hygiene)
git add <files>
git commit -m "..."
# ... repeat for each commit unit ...

# 5. Implementation done — push and open PR (see git-workflow skill for PR format)
git push -u origin refactor/some-feature
gh pr create --title "..." --body "..."

# 6. Squash merge
gh pr merge --squash --delete-branch
```

## Reference materials added during brainstorming

If the user adds reference documents (external pattern guides, source articles) to the working tree during brainstorming and the spec links to them, commit the references *before* the spec commit so the spec's links resolve throughout the branch history.

```bash
# 먼저 참고 문서 커밋
git add docs/some_reference_pattern.md
git commit -m "docs: <topic> 참고 문서 추가"

# 그다음 참고 문서를 가리키는 설계서 커밋
git add docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
git commit -m "docs: <topic> 설계서 추가"
```

## Discarding mid-brainstorm

If the user decides not to proceed and the branch hasn't been pushed:

```bash
git checkout main
git branch -D refactor/some-feature
```

If the branch was already pushed (e.g., a draft PR was opened for early visibility across sessions), close the PR without merging and delete the remote branch.

## Scope boundary

This pattern applies only when the spec is the *prelude* to implementation in the same iteration. Updating a pre-existing spec document with no implementation following is a normal `docs/` PR — small, atomic, lands on its own. Don't force the spec-first pattern onto doc-only changes.

## Long-running brainstorms: draft PR

The default is "don't push until implementation produces meaningful commits" — this prevents an empty PR (spec only, no implementation) from signalling "ready for review" prematurely. However, if the brainstorming stretches over multiple sessions or you want the spec visible early, open the PR as **draft** (`gh pr create --draft ...`) and flip to ready once implementation is complete. See the git-workflow skill's "Draft PRs" subsection for the general draft PR criteria.
