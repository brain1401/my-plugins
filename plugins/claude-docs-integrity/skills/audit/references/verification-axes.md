# Verification Axes Reference

Canonical specification for the four verification axes. This document is the single source of truth for scope, methodology, output format, and sprint contract templates. Agent definitions (planner, generator, evaluator) derive from this specification. When updating verification methodology, update this file first, then propagate to agent definitions as needed.

## Axis 1: Factual Consistency

### Scope
- Document ↔ Document: Every factual claim in CLAUDE.md compared against every rules file, and vice versa
- Document ↔ Code: Every factual claim in any documentation file compared against the actual source code

### What to Check
- Configuration values (ports, file paths, feature flags, default values)
- Frontmatter schema fields (types, defaults, required/optional status)
- Build pipeline steps and their order
- Architectural claims (which component does what, which file lives where)
- Behavioral descriptions (what happens when X is set to Y)

### Finding Classification
- **CONTRADICTION**: Two documents state different things about the same fact
- **INACCURACY**: A document states something that does not match the actual source code
- **MISLEADING**: Technically true but phrased in a way that could cause misunderstanding

### Output Format
```markdown
## Factual Consistency Findings

### Inaccuracies
[INACCURACY] <description>
  - Source: <document and line>
  - Actual: <what the code shows>
  - Impact: <how this could cause problems>

### Contradictions
[CONTRADICTION] <description>
  - Source A: <document and what it says>
  - Source B: <document and what it says>
  - Impact: <consequence>

### Misleading
[MISLEADING] <description>
  - Source: <document and what it says>
  - Reality: <the nuance that's missing>
  - Impact: <potential misunderstanding>

### Verified Consistent
- <fact 1> — consistent across <list of documents>
- <fact 2> — ...
```

### Sprint Contract Template
```markdown
## Done Conditions
- [ ] Every factual claim in CLAUDE.md cross-checked against all rules files
- [ ] Every factual claim in all documents cross-checked against source code
- [ ] Each finding classified (CONTRADICTION / INACCURACY / MISLEADING)
- [ ] Impact assessment per finding
- [ ] List of verified consistent facts provided
```

---

## Axis 2: Redundancy

### Scope
- CLAUDE.md content compared against each rules file's content
- Identify information that exists in both and assess whether duplication is justified

### Duplication Categories
- **EXACT DUPLICATE**: Same fact at the same detail level in both locations
- **EXPANDED IN RULE**: CLAUDE.md has brief mention, rule has detailed explanation (often acceptable as pointer-to-detail pattern)
- **EXPANDED IN CLAUDE.MD**: CLAUDE.md has more detail than the rule (usually wrong; rules should hold the detail)

### Recommendation Types
- **KEEP BOTH**: CLAUDE.md serves as pointer, rule has the depth (ideal pattern)
- **TRIM CLAUDE.MD**: Remove detail from CLAUDE.md, keep a pointer to the rule
- **TRIM RULE**: Information belongs at project level, not in a path-triggered rule
- **MERGE**: Consolidate into one location

### Output Format
```markdown
## Redundancy Findings

| # | Information | CLAUDE.md | Rules File | Duplicate Type | Recommendation |
|---|-------------|-----------|------------|----------------|----------------|
| 1 | ... | line X | file.md | EXACT DUPLICATE | TRIM CLAUDE.MD |
```

### Sprint Contract Template
```markdown
## Done Conditions
- [ ] Every discrete fact in CLAUDE.md checked against all rules files
- [ ] Every discrete fact in each rules file checked against CLAUDE.md
- [ ] Each duplicate categorized (EXACT / EXPANDED IN RULE / EXPANDED IN CLAUDE.MD)
- [ ] Recommendation per duplicate (KEEP BOTH / TRIM CLAUDE.MD / TRIM RULE / MERGE)
- [ ] Items unique to CLAUDE.md listed (confirm they belong there)
- [ ] Items unique to rules files listed (confirm they belong there)
```

---

## Axis 3: Path Validity

### Scope
- Every file path in rules file YAML frontmatter `paths:` arrays
- Every file path referenced in rules file body content
- Every file path referenced in CLAUDE.md

### What to Check
- **Existence**: Does the referenced path actually exist in the codebase?
- **Glob matches**: For glob patterns (`**/*.ts`), do matching files actually exist?
- **Completeness**: Are there important files in covered directories that should be in a rule's path trigger but aren't?
- **Orphan detection**: Important project files that match no rule's path triggers

### Output Format
```markdown
## Path Validity Findings

### Path Trigger Verification
| # | Rule File | Path | Status | Notes |
|---|-----------|------|--------|-------|
| 1 | rule.md | src/utils/foo.ts | EXISTS | |
| 2 | rule.md | src/bar/** | PARTIAL | 3 files match, but src/bar/baz.ts is uncovered |
| 3 | rule.md | src/missing.ts | MISSING | File does not exist |

### Body Reference Verification
| # | Document | Referenced Path | Status |
|---|----------|----------------|--------|

### Orphan Files
| File | Relevant Domain | Suggested Rule |
|------|----------------|----------------|

### Coverage Gaps
| Directory | Uncovered Files | Suggested Rule |
|-----------|----------------|----------------|
```

### Sprint Contract Template
```markdown
## Done Conditions
- [ ] Every path in every rules file frontmatter verified (EXISTS/MISSING/PARTIAL)
- [ ] Every file path in rules file bodies verified
- [ ] Every file path in CLAUDE.md verified
- [ ] Glob patterns expanded and all matches listed
- [ ] Orphan files identified (important files with no rule coverage)
- [ ] Coverage gap analysis per directory
```

---

## Axis 4: Cross-Reference Integrity

### Scope
- Inter-rule references (rules that mention other rules by name)
- Path overlap analysis (files that trigger multiple rules)
- Dependency mapping between rules

### What to Check
- **Reference accuracy**: When rule A mentions rule B, does rule B exist with that exact name?
- **Bidirectional references**: If rule A references rule B, should rule B reference rule A?
- **Multi-trigger analysis**: For each file, which rules fire? Is the combination beneficial or noisy?
- **Conflict detection**: Could two rules give contradictory guidance when both triggered?
- **Asymmetric coupling**: Rule A mentions a concept owned by rule B, but rule B doesn't acknowledge the coupling

### Output Format
```markdown
## Cross-Reference Integrity Findings

### Inter-Rule References
| From | To | Direction | Status |
|------|----|-----------|--------|
| rule-a.md | rule-b.md | Forward | CORRECT |
| rule-b.md | rule-a.md | Reverse | MISSING (asymmetric) |

### Multi-Trigger Analysis
| File/Pattern | Rules That Fire | Assessment |
|--------------|----------------|------------|
| src/layouts/PostDetails.astro | design-context, frontend-verification, client-side-scripts, markdown-pipeline | BENIGN (complementary) |

### Path Overlap Map
[Dependency graph of rules showing shared paths and references]

### Conflicts
[Any contradictory guidance between co-triggered rules]
```

### Sprint Contract Template
```markdown
## Done Conditions
- [ ] All inter-rule references verified (name match, file existence)
- [ ] Bidirectional reference check (asymmetric references flagged)
- [ ] Every file in project mapped to its triggering rules
- [ ] Multi-trigger cases assessed (BENIGN / NOISY / CONFLICT)
- [ ] Dependency graph produced
- [ ] No unresolved conflicts between co-triggered rules
```
