# ctx7 Query Strategy and Self-Check Guide

## Query Strategy: Don't Stop at the First Result

A common failure mode is querying once, getting a partial or irrelevant result, and then falling back to training data. This defeats the purpose of the lookup. Follow this escalation pattern:

1. **First query: direct and specific** — use the exact API name or feature you're looking for.
   - Example: `"updateTag revalidateTag cache invalidation"`
2. **Second query: broaden if needed** — if the first query misses, try related concepts or the feature category.
   - Example: `"cache invalidation server actions use cache"`
3. **Third query: search for what's new** — explicitly ask about new or changed APIs in the current version.
   - Example: `"new APIs next.js 15 caching breaking changes"`

Do not assume your first query covers everything. Libraries often have multiple APIs for similar tasks, and the one you don't know about may be the correct one for your use case.

## Verify Your Chosen API Is the Best Fit

After finding an API that works, ask yourself: **"Is there a more specific API designed for exactly this use case?"** General-purpose APIs often have specialized alternatives that handle edge cases better.

For example:
- `revalidateTag` works for cache invalidation, but `updateTag` exists specifically for read-your-own-writes scenarios
- `'use cache'` works for caching, but `'use cache: remote'` exists specifically for cross-instance cache sharing in serverless

If the task description mentions a specific constraint (e.g., "serverless", "immediate consistency", "cross-instance"), query the docs for that constraint explicitly before settling on a general solution.

## Tips for Effective Queries

- Be specific with your topic. "next.config.js cacheComponents" is far better than "config".
- Include key terms from the error message in your topic.
- Check the project's `package.json` or config files for the exact version first, then reference docs for that version.
- When the task has specific requirements (e.g., "shared across instances", "immediate invalidation"), include those requirements as keywords in your query.

## Self-Check Questions

If you can answer "yes" to any of these during work, you should use ctx7:

1. Is this not the first time I've seen this error? Am I hitting the same class of error repeatedly?
2. Am I uncertain whether this API/option/config behaves exactly this way in the current project's version?
3. Am I unsure whether the code I'm about to write follows the pattern recommended by the official docs?
4. Do I lack concrete evidence that my planned approach will actually work?
5. Could there be a more specific API designed for exactly this use case that I'm not aware of?
