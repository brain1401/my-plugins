---
name: audit
description: >-
  This skill should be used when the user asks to "audit CLAUDE.md",
  "check CLAUDE.md consistency", "verify rules files", "check docs integrity",
  "validate CLAUDE.md and rules", "find duplicates in CLAUDE.md",
  "check if rules paths are valid", "CLAUDE.md 검증", "rules 정합성 체크",
  or wants to verify coherence between CLAUDE.md and .claude/rules/ files.
  Triggers on documentation quality audits, rule file validation, or cross-reference checking.
argument-hint: "[optional: 'paths' | 'consistency' | 'redundancy' | 'crossref' | omit for full audit]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Agent"]
---

# CLAUDE.md & Rules Integrity Audit

Orchestrate a comprehensive integrity audit of CLAUDE.md and `.claude/rules/` files using a three-agent pipeline: **Planner → Generator → Evaluator**.

## Workflow Overview

```
Planner (discovery + plan)
    ↓ audit-plan.md
Generator (sprint contracts + parallel verification)
    ↓ sprint-contracts/*.md + findings/*.md
Evaluator (validation + report)
    ↓ evaluation-report.md
User (approve → apply fixes → cleanup)
```

## Phase 1: Setup

Create working directory `.claude-docs-integrity/` in the project root for inter-agent file communication. All intermediate artifacts live here and are cleaned up after the audit.

## Phase 2: Planning

Spawn the **planner** agent using the Agent tool (`subagent_type: "claude-docs-integrity:planner"`). In the prompt, provide the project root path and any focus area argument.

The planner discovers all documentation files, analyzes project structure, and writes `audit-plan.md` defining verification axes with expected deliverables. All agents read from and write to the `.claude-docs-integrity/` working directory — pass file paths, not content, between phases.

**Critical constraint**: The plan defines WHAT to verify (deliverables and scope), never HOW (implementation details). Overly specific technical prescriptions from the planner propagate errors to all downstream work.

After the planner completes, read `.claude-docs-integrity/audit-plan.md` to confirm scope before proceeding.

## Phase 3: Generation

Spawn the **generator** agent (`subagent_type: "claude-docs-integrity:generator"`). In the prompt, state the path to the audit plan file (`.claude-docs-integrity/audit-plan.md`). The generator reads it from disk.

The generator:
1. Writes sprint contracts (`sprint-contracts/{axis}.md`) with negotiated done conditions
2. Dispatches parallel subagents per verification axis
3. Collects results into `findings/{axis}.md`

## Phase 4: Evaluation

Spawn the **evaluator** agent (`subagent_type: "claude-docs-integrity:evaluator"`). In the prompt, state the paths to sprint contracts and findings directories. The evaluator reads them from disk.

The evaluator independently validates findings, cross-checks for inter-axis conflicts, spot-checks claims against actual code, and writes `evaluation-report.md`.

## Phase 5: Report & Fix

Read `evaluation-report.md` and present to the user:
- Summary table (issue count by severity: P0/P1/P2/P3)
- Detailed findings per axis
- Recommended fixes with before/after diffs

On user approval, apply fixes with the Edit tool. After each fix, verify correctness.

## Phase 6: Cleanup

Delete `.claude-docs-integrity/` directory.

## Rework Protocol

If the evaluator reports unmet sprint contract conditions:
1. Re-spawn generator with evaluator's feedback (only failed axes)
2. Re-spawn evaluator for re-validation
3. Maximum **1 rework iteration**. If still unmet, present partial results to user with explanation.

## Focus Mode

When the user specifies a focus area via argument, limit audit scope:

| Argument | Scope |
|----------|-------|
| `paths` | Path validity only |
| `consistency` | Factual consistency only |
| `redundancy` | Redundancy analysis only |
| `crossref` | Cross-reference integrity only |
| _(omitted)_ | Full audit across all axes |

Pass the focus area to the planner so it scopes the plan accordingly.

## File Communication Protocol

```
.claude-docs-integrity/
├── audit-plan.md              # Planner → Generator
├── sprint-contracts/
│   ├── factual.md             # Generator ↔ Evaluator
│   ├── redundancy.md
│   ├── paths.md
│   └── crossref.md
├── findings/
│   ├── factual.md             # Generator → Evaluator
│   ├── redundancy.md
│   ├── paths.md
│   └── crossref.md
└── evaluation-report.md       # Evaluator → User
```

## Additional Resources

For detailed verification methodology per axis (scope, methodology, output format, done condition templates):
- **`references/verification-axes.md`**
