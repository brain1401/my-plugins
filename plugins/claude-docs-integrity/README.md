# claude-docs-integrity

Audit and fix consistency, redundancy, validity, and cross-references across CLAUDE.md and `.claude/rules/` files.

## What It Does

Runs a three-agent pipeline (Planner → Generator → Evaluator) to verify documentation integrity:

| Axis | What It Checks |
|------|---------------|
| **Factual Consistency** | Do CLAUDE.md, rules files, and actual source code agree on facts? |
| **Redundancy** | Is information duplicated between CLAUDE.md and rules? Where should each fact live? |
| **Path Validity** | Do all file paths referenced in rules actually exist? Are important files uncovered? |
| **Cross-Reference Integrity** | Do rules reference each other correctly? Are there path overlaps or conflicts? |

## Components

### Skill

- **`audit`** — Full audit orchestrator. Invoke with `/claude-docs-integrity:audit`. Optional focus: `paths`, `consistency`, `redundancy`, `crossref`.

### Agents

| Agent | Role | Trigger |
|-------|------|---------|
| **planner** | Discovers files, creates high-level audit plan | First step in audit pipeline |
| **generator** | Executes verification axes with parallel subagents | After planner completes |
| **evaluator** | Validates findings, produces prioritized report | After generator completes |
| **integrity-check** | Quick check after CLAUDE.md or rules edits | Auto-triggered after documentation changes |

## Usage

### Full Audit

```
/claude-docs-integrity:audit
```

### Focused Audit

```
/claude-docs-integrity:audit paths
/claude-docs-integrity:audit consistency
```

### Quick Check (automatic)

The `integrity-check` agent triggers automatically when CLAUDE.md or `.claude/rules/` files are modified.

## Architecture

```
User → audit skill → Planner Agent
                         ↓ audit-plan.md
                     Generator Agent
                         ↓ sprint-contracts/ + findings/
                     Evaluator Agent
                         ↓ evaluation-report.md
                     User (approve fixes)
```

**Key design decisions:**

- **Planner defines WHAT, not HOW** — Prevents implementation errors from propagating downstream
- **Sprint contracts** — Generator and Evaluator share explicit done conditions for each verification axis
- **File-based communication** — Agents write to `.claude-docs-integrity/` directory, which is cleaned up after completion
- **Parallel subagents** — Generator dispatches one subagent per verification axis for concurrent execution
- **Independent evaluation** — Evaluator spot-checks generator claims against actual code, doesn't rubber-stamp

## Installation

```bash
claude --plugin-dir /path/to/claude-docs-integrity
```

Or add to your Claude Code plugins configuration.
