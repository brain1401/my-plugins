---
name: inflearn-script-extractor
description: >
  Automatically extracts all transcripts (subtitles) from Inflearn course videos and generates structured documents.
  Uses Playwright MCP to collect subtitle data from lecture pages, outputting section-organized Markdown + JSON + individual files.
  Trigger this skill when the user mentions "인프런 강의 스크립트 추출", "인프런 자막 뽑아줘", "인프런 강의 내용 정리",
  "inflearn transcript", "강의 스크립트 문서화", or provides an Inflearn course URL or courseId.
  Also trigger when any inflearn.com URL is mentioned in the context of transcript or script extraction.
---

# Inflearn Lecture Script Extractor

Automated workflow to extract transcripts (subtitles) from all videos in an Inflearn course and produce structured documents.

## Prerequisites

- **Playwright MCP** server must be connected
- User must be **logged in** to Inflearn (required for paid course access)
- User must be **enrolled** in the target course to access subtitles

## Overall Workflow

```
1. Verify login → 2. Obtain courseId → 3. Fetch lecture list via Curriculum API
→ 4. Collect subtitles in batches → 5. Generate outputs (MD + JSON + individual files)
```

---

## Phase 1: Login & Course Access

### Extracting courseId

Extract the courseId from the URL provided by the user. Inflearn URL patterns:

- `https://www.inflearn.com/course/{slug}/dashboard?cid={courseId}` → `cid` parameter
- `https://www.inflearn.com/courses/lecture?courseId={courseId}&...` → `courseId` parameter

If the URL does not contain a courseId, navigate to the URL and locate the courseId from the dashboard page.

### Login Handling

Subtitle data is only accessible for enrolled courses, so login is mandatory.
Check login status in the Playwright MCP browser and, if needed, open the login dialog for the user to authenticate.
Never ask for or accept credentials (email/password) directly.

**Login verification procedure:**

1. Navigate to `https://www.inflearn.com`
2. Take a snapshot and check for the presence of a "로그인" (Login) button
   - If the snapshot is too large, use Bash grep to search for the `로그인` keyword
3. If the login button exists → not logged in, proceed with the login flow below
4. If the login button is absent → already logged in, proceed to Phase 2

**Login flow when not authenticated:**

1. Find and click the "로그인" button ref from the snapshot
2. Once the login dialog opens, inform the user:
   > "Inflearn login is required. The login dialog is now open — please log in using email/password or social login (Google, GitHub, Kakao, etc.). Let me know when you're done."
3. After the user confirms login, take another snapshot to verify successful authentication
4. If login failed, prompt the user to retry

**Login dialog structure (reference):**

The Inflearn login dialog contains:
- Email input field (`textbox "이메일"`)
- Password input field (`textbox "비밀번호"`)
- Login button (`button "로그인"`)
- Social login buttons: Google, GitHub, Apple, Kakao

**Accessing unenrolled courses:**

If the user is logged in but not enrolled in the course, the Curriculum API will still respond normally,
but the script tab will show no subtitles during collection.
If the first lecture returns empty subtitle data, inform the user:
> "Unable to retrieve subtitle data. Please verify that you are enrolled in this course."

---

## Phase 2: Curriculum Collection

Fetch the full course structure via API.

### Curriculum API

```
GET https://course-api.inflearn.com/client/api/v2/courses/{courseId}/curriculum?lang=ko
```

This API must be called via `fetch()` inside `page.evaluate` on an Inflearn lecture page.
It requires browser session cookies — calling it externally will fail authentication.

### Response Structure

```json
{
  "data": {
    "curriculum": [
      {
        "id": 419581,
        "title": "Section title",
        "units": [
          {
            "id": 419582,        // unitId — the key identifier
            "title": "Lecture title",
            "type": "LECTURE",    // LECTURE, QUIZ, etc.
            "runtime": 612,      // duration in seconds
            "hasAttachment": false
          }
        ]
      }
    ]
  }
}
```

### Filtering Criteria

- Only collect units where `type === "LECTURE"` AND `runtime > 0`
- Exclude QUIZ, attachment-only units (runtime=0), etc.

---

## Phase 3: Subtitle Collection (Critical)

This is the most important and delicate phase. Follow the pattern below exactly.

### Subtitle Data Source

Inflearn serves subtitles via CloudFront signed URLs (`vod.inflearn.com/videos/{vodId}/encrypted/subtitles/json?Policy=...`).
The signing parameters are generated dynamically on page load, so the URL cannot be constructed manually.
Therefore, use the **page navigation + network response interception** approach.

### Proven Collection Pattern

For each lecture, collect subtitles using this pattern:

```javascript
// Execute inside Playwright run_code
async (page) => {
  const units = [ /* array of target units */ ];
  const results = [];

  for (const unit of units) {
    try {
      let subtitleData = null;

      // 1. Register response handler BEFORE navigation
      const handler = async (response) => {
        if (response.url().includes('subtitles/json')) {
          try { subtitleData = await response.json(); } catch(e) {}
        }
      };
      page.on('response', handler);

      // 2. Navigate directly to the script tab
      await page.goto(
        `https://www.inflearn.com/courses/lecture?courseId=${courseId}&tab=script&type=LECTURE&unitId=${unit.unitId}&subtitleLanguage=ko`,
        { waitUntil: 'load', timeout: 20000 }
      );

      // 3. Wait for subtitle response — minimum 5 seconds
      await page.waitForTimeout(5000);

      // 4. Unregister handler
      page.off('response', handler);

      if (subtitleData && Array.isArray(subtitleData)) {
        results.push({
          ...unit,
          entries: subtitleData.length,
          transcript: subtitleData.map(e => e.text).join(' ')
        });
      }
    } catch(e) {
      results.push({ ...unit, entries: 0, transcript: '', error: e.message });
    }
  }
  return results;
};
```

### Critical Gotchas

| Item | Correct | Wrong |
|------|---------|-------|
| waitUntil | `'load'` | `'networkidle'` (causes timeout) |
| Timeout method | `page.waitForTimeout(5000)` | `setTimeout()` (undefined in run_code) |
| Batch size | **10–12 units** per batch | All at once (MCP connection drops) |
| Handler registration | **Before** `goto()` | After `goto()` (misses fast responses) |
| Handler cleanup | `page.off()` after each unit | Never unregistered (handlers accumulate) |

### Batch Processing

Process 10–12 units per batch to maintain MCP connection stability.
Save each batch's results immediately to a local JSON file so progress is not lost if the connection drops.

```
Batch 1: units 1–12 → save to batch_temp.json
Batch 2: units 13–24 → merge into batch_temp.json
...repeat...
```

### Retrying Failed Units

Some units may fail subtitle collection (e.g., timeout).
After all batches are complete, gather the failed units and retry them once.

---

## Phase 4: Output Generation

Once collection is complete, generate three output formats.

### 1. Full Markdown Document (`{courseName}_full_script.md`)

```markdown
# {Course Name} - Full Script

> Complete transcript from Inflearn course

---

## Section 1. {Section Title}

### 1. {Lecture Title}

{Full transcript text}

### 2. {Lecture Title}

{Full transcript text}

## Section 2. {Section Title}
...
```

### 2. Raw JSON Data (`{courseName}_scripts.json`)

Preserve all collected data in structured JSON:

```json
{
  "courseName": "Course Name",
  "courseId": 341151,
  "extractedAt": "2026-03-29",
  "sections": [
    {
      "id": 419581,
      "title": "Section Title",
      "lectures": [
        {
          "unitId": 419582,
          "title": "Lecture Title",
          "runtime": 612,
          "entries": 174,
          "transcript": "Full text..."
        }
      ]
    }
  ]
}
```

### 3. Individual Lecture Files (`scripts/{sectionNum}_{lectureNum}_{title}.md`)

Save each lecture as a separate markdown file:

```
scripts/
├── 01_01_lecture_intro.md
├── 01_02_course_background.md
├── 02_01_dont_write_OOO.md
└── ...
```

### Output Directory Structure

```
{output_dir}/
├── {courseName}_full_script.md
├── {courseName}_scripts.json
└── scripts/
    ├── 01_01_{title}.md
    ├── 01_02_{title}.md
    └── ...
```

---

## Phase 5: Progress Reporting

Report progress to the user at each stage:

- After curriculum collection: "Found N sections, M lectures"
- After each batch: "Collected N/M (success rate X%)"
- After completion: provide a summary table with results

---

## Extending to Other Lecture Platforms

The core patterns in this skill can be applied to other lecture platforms.
Refer to `references/extension-guide.md` for the extension guide.

Key abstraction points:
1. **Curriculum API**: Find each platform's lecture listing API
2. **Subtitle source**: Platforms vary in how subtitles are served (API, DOM, VTT files, etc.)
3. **Authentication**: Session cookies, tokens, etc. — platform-specific auth mechanisms
4. **Page structure**: SPA routing, subtitle loading timing, etc.
