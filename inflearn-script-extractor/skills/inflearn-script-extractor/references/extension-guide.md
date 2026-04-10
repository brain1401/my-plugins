# Extending to Other Lecture Platforms

How to apply the patterns from this skill to other lecture platforms.

## Core Pattern

The fundamental flow for subtitle extraction is the same on any platform:

```
1. Login → 2. Obtain lecture list → 3. Collect subtitles per lecture → 4. Generate documents
```

## How to Discover Subtitle Sources per Platform

### Step 1: Analyze Network Requests

Register a `page.on('response')` handler in Playwright MCP's `browser_run_code`,
then load the lecture page and capture subtitle-related responses.

```javascript
// Filter by subtitle-related keywords
const keywords = ['subtitle', 'caption', 'transcript', 'script', 'vtt', 'srt', 'json'];
page.on('response', async (response) => {
  const url = response.url();
  if (keywords.some(kw => url.includes(kw))) {
    console.log(url, response.status());
  }
});
```

### Step 2: Discover API Endpoints

Monitor API calls that occur during lecture page load.
Pay attention to requests containing keywords like `course`, `curriculum`, `lesson`, `chapter`, `unit`.

### Step 3: Identify Authentication Method

Most platforms use one of the following:
- **Session cookies**: Automatically included when using `fetch()` within the browser context
- **Bearer tokens**: Requires adding a token to headers (extract from localStorage or cookies)
- **Signed URLs**: CDN signing like CloudFront (Inflearn's approach) — dynamically generated on page load

## Common Subtitle Formats

| Format | Characteristics | Parsing Method |
|--------|----------------|----------------|
| JSON array | `[{start, end, text}]` | Parse directly |
| WebVTT (.vtt) | Text-based subtitle format | Parse with regex |
| SRT (.srt) | Number + timecode + text | Line-by-line parsing |
| DOM rendering | Displayed as HTML elements | DOM queries |

## Platform-Specific Hints

### Udemy
- Subtitles are often served in `.vtt` format
- API: `https://www.udemy.com/api-2.0/courses/{id}/...`
- Auth: Bearer token (from cookie's access_token)

### Coursera
- Subtitles are served as separate `.srt` files
- Lecture list: `https://www.coursera.org/api/onDemandLectureVideos.v1/...`

### YouTube (lecture playlists)
- Subtitle API is well-documented
- Tools like `youtube-transcript-api` are available

## Universal Playwright MCP Gotchas

These apply regardless of platform:

1. **Use `waitUntil: 'load'`** — `networkidle` causes timeouts in SPAs
2. **Use `page.waitForTimeout()`** — `setTimeout()` is undefined in the `run_code` context
3. **Batch size of 10–12** — for MCP connection stability
4. **Register response handlers before navigation** — registering after may miss fast responses
5. **Save results to file immediately** — guard against MCP connection drops
