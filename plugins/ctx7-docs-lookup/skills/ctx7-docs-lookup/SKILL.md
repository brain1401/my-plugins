---
name: ctx7-docs-lookup
description: This skill should be used when encountering repeated errors during coding (same error 2+ times), or when uncertain about library API behavior in the project's versions. Triggers on phrases like "look up the docs", "check official documentation", "this error keeps happening", "does this API exist in version Y". Also relevant when adopting unfamiliar libraries, verifying API signatures, handling migrations, or writing version-specific config. Uses ctx7 (context7) to query official documentation.
---

# ctx7 Official Documentation Lookup Guide

## Why This Skill Exists

LLM training data contains outdated APIs, removed options, and behaviors that changed between versions. Relying solely on this knowledge leads to calling non-existent functions, using deprecated patterns, or generating code incompatible with the project's actual library versions. The result is wasted time debugging phantom issues and plans built on false assumptions.

ctx7 (context7) can query **official documentation matching the exact version** of libraries used in the current project. Work from facts, not guesses.

## When NOT to Use ctx7

Do not look up documentation for APIs and patterns you are fully confident about. ctx7 lookups cost time and tokens. If the answer is obvious and the API is stable, just write the code.

**Skip ctx7 when ALL of the following are true:**

- The API is well-established and has not changed across recent major versions (e.g., `useState`, `useEffect`, `fetch`, `Array.map`, basic DOM APIs)
- You are fully confident in the exact signature, behavior, and usage pattern
- The task does not involve version-specific features, recent additions, or framework-level APIs that change between releases
- There are no special constraints in the task (e.g., "serverless", "edge runtime", "cross-instance") that might require a specialized variant

Examples of when to **skip** ctx7:
- Writing a React component with `useState` and `useEffect`
- Using native `fetch`, `Promise`, `AbortController`
- Standard TypeScript patterns, basic HTML/CSS
- Well-known utility library APIs (lodash, date-fns basics)

Examples of when you **must** use ctx7:
- Framework-specific caching, routing, or rendering APIs (`use cache`, `revalidateTag`, App Router patterns)
- APIs that have changed in recent major versions (`forwardRef` in React 19, `@theme` in Tailwind v4)
- New or recently added APIs you haven't used before
- Configuration files for specific framework versions
- Anything where the task mentions deployment-specific constraints

**When in doubt, consider: "Has this API changed in any recent major version?" If yes, look it up. If no, just write the code.**

## Trigger Conditions

### Condition 1: Repeated Errors During Implementation

When writing or debugging code, ctx7 lookup is **mandatory** if any of the following occur:

- The same or similar error appears **2 or more times**
- The root cause of an error message is unclear
- The exact signature, options, or behavior of a library/framework API is uncertain
- An attempted fix did not work and the reason is unknown

Continuing to guess-and-retry in these situations is a waste of time. Stop and consult the official docs via ctx7 immediately.

### Condition 2: Insufficient Confidence During Planning

When building an implementation plan or making design decisions, ctx7 lookup is **mandatory** if any of the following apply:

- You are not confident your knowledge accurately applies to the library versions in the current project
- You are unsure whether a specific API or config option is available in the current version
- You lack confidence that the planned implementation will work correctly
- You are introducing a new library or using a feature for the first time
- The task involves migration or version upgrade work

Planning based on "this will probably work" can cause the entire plan to collapse during implementation. If you are not certain, check the docs first.

## How to Use context7

### Step 0: Understand the Project First

Before querying docs, check what you're actually working with:

1. Read `package.json` (or equivalent dependency file) to identify the **exact versions** of libraries in use.
2. Note the project's tech stack — framework, language, deployment target (serverless, edge, etc.).
3. Use version-specific library IDs when available (e.g., `/vercel/next.js/v15.1.8` instead of `/vercel/next.js`).

This context shapes your queries. A project on Next.js 15 with Vercel serverless deployment needs different docs than one on Next.js 14 with a Node.js server. Without this step, you may find correct documentation for the wrong version.

### Query by CTX7_MODE

The `$CTX7_MODE` environment variable is automatically set at session start. Check its value and follow the corresponding path below.

### If `CTX7_MODE=mcp` — MCP Tools Available

Use MCP tools directly:

1. **Resolve the library ID** — call `mcp__context7__resolve-library-id` with the library name (e.g., "nextjs", "react", "prisma")
2. **Query the documentation** — call `mcp__context7__query-docs` with the resolved library ID and a detailed, descriptive topic. Include version number and project context in your query when relevant.
3. **Evaluate the results** — check whether the docs confirm your approach or reveal a better/newer API.
4. **If results are insufficient, query again with different keywords** — try at least 2-3 different queries before concluding that the information isn't available.

### If `CTX7_MODE=skill` — Use CLI/Skill

MCP is not configured. Use the `find-docs` skill instead:

1. **Invoke the skill** — call the `find-docs` skill via the Skill tool with the library name and topic as arguments.
2. **Evaluate the results** — same as MCP path: verify the docs match your use case.
3. **If results are insufficient, invoke again with different keywords** — rephrase, broaden, or narrow your search terms.

### If `CTX7_MODE=unknown` or Not Set — Fallback

The detection could not determine which method is available. Try in this order:

1. **Try MCP first** — call `mcp__context7__resolve-library-id`. If it succeeds, continue with MCP tools.
2. **If MCP fails** (tool not found / unknown tool error), **try the skill** — invoke `find-docs` via the Skill tool.
3. **If both fail**, inform the user: "context7 is not available. Add a context7 MCP server to .mcp.json, or install a plugin that provides the find-docs skill."

## Important Notes

- ctx7 is a tool, not a silver bullet. After consulting the docs, you still need to adapt findings to the project's context.
- If documentation conflicts with the project's existing patterns or conventions, prioritize the project's established approach while using the docs as a reference to adjust.
- You do not need to use ctx7 for every API call. Querying things you already know with certainty is inefficient. The key is to use it when you **don't know**, when you **lack confidence**, or when **errors keep repeating**.

## Reference Files

For detailed query techniques and self-check guidelines:

- **`references/query-strategy.md`** — Query escalation patterns, API fit verification, effective query tips, and self-check questions
