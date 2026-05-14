# Quran App — Rendering Workflow

## Data files

| File | Role | Source |
|------|------|--------|
| `qpc-v1-glyph-codes-wbw.json` | word-by-word glyph codes for QCF font display | replaces `mushaf.txt` |
| `imlaei.json` | word-by-word readable Arabic text | replaces `quran-uthmani.json` |
| `pages.json` | page layout — which lines are on which page, line types, word ID ranges | replaces `mushaf.txt` page structure |
| `surah_info.json` | surah names for headers | kept as-is |
| `hifz_data.json` | trigram → similar ayahs lookup | kept as-is |

### Key relationship

Both `qpc-v1-glyph-codes-wbw.json` and `imlaei.json` share the exact same keys:
- Key format: `"surah:ayah:word"` (e.g., `"1:1:3"`)
- Each entry also has a sequential numeric `id` (1–83668)
- The `id` is the correct Quranic order — **never use string-key order** (JS object keys sort alphabetically, placing `"10:1:1"` before `"2:1:1"`)

`pages.json` uses these `id` values to define page lines:
```json
{"line_number":2,"line_type":"ayah","first_word_id":1,"last_word_id":5,"page_number":1}
```

---

## Initialization (`index.html → js/mushaf-app.js:init()`)

```
init()
├── load bismillah font (font-family "QCF_Bismillah" from QCF_P001.woff2)
├── QuranData.load()
│   ├── fetch all 5 JSON files in parallel (Promise.all)
│   ├── sort qpc entries by id (correct order)
│   ├── for each entry:
│   │   ├── wordsById.set(id, {surah, ayah, word, glyph, text})
│   │   ├── ayahWords.get("surah:ayah").push(word)        — all words
│   │   └── ayahWordsNoMarker.get("surah:ayah").push(word) — non-marker only
│   ├── sort each ayah's word array by word position
│   └── parse pages.json: pageLines.set(page, [{lineType, firstWordId, ...}])
├── _buildAyahPageMap()
│   └── iterate all pages/lines to build: "surah:ayah" → pageNumber
├── _setupEvents()
│   └── wire navigation buttons, copy button, keyboard events, selectionchange
├── _getInitialPage() — read #page=N from URL
└── renderPage(currentPage)
```

---

## Page rendering (`renderPage(page)`)

### Step 1 — Reset state
```
selectedAyahKey = null
disable copy button
hide tooltip
update URL hash to #page=N
```

### Step 2 — Load font (non-blocking)
```
_loadFont(page)
├── fetch qcf_fonts/QCF_P{NNN}.woff2
├── convert to base64
└── inject @font-face with font-family "QCF_P{page}"
```

### Step 3 — Get page content
```
lines = QuranData.getPageLines(page)
```

`getPageLines()` looks up `pageLines.get(page)` and for each "ayah" line calls `getWordsInRange(firstWordId, lastWordId)` which iterates `wordsById` from `firstWordId` to `lastWordId` and collects the word objects. This resolves numeric ID ranges back into actual word data.

### Step 4 — Build HTML per line

For each line in the page:

**Line type: `surah_name`**
```
→ <div class="surah-header">سورة {name}</div>
```
The surah number comes from `pages.json`. The name is looked up from `surah_info.json`.

**Line type: `basmallah`**
```
→ <span class="bismillah">ﭑﭒﭓﭔ</span>
```
Rendered with `QCF_Bismillah` font (loaded once at startup).

**Line type: `ayah`**
```
→ _renderAyahLine(words)
```

### Step 5 — Split line into ayahs (`_renderAyahLine`)

A single physical page line can contain words from **multiple ayahs** (separated by ayah-number marker words).

Splitting logic:
```
groups = []
current = []
for each word w in line.words:
    if current not empty AND current[0].ayah != w.ayah:
        → start new ayah group
    push w into current
push last current group
```

Each group contains all words (including the ayah-marker word) that share the same `ayah` number.

### Step 6 — Render each ayah group

For normal mode:
```
→ <span class="ayah" data-surah="N" data-ayah="M" data-key="N:M" onclick="selectAyah">
    <span class="word" data-word="1">glyph1</span>
    <span class="word" data-word="2">glyph2</span>
    ...
  </span>
```

Each word gets its own `<span class="word">`. The `data-word` attribute stores the word's position within the ayah, which enables the selection-based copy feature (finds which word spans intersect the user's text selection).

**When hifz mode is on and the ayah has matches:**
```
→ _renderHifzWords(group, surah, ayah)
```

Instead of flat word spans, matching trigram blocks are wrapped in `<span class="hifz-block" data-group="...">` with tooltip data attached.

### Step 7 — Insert into DOM
```
content.innerHTML = html
```

---

## Hifz mode

### Step 1 — Get matching trigrams (`_getMatchingGroups`)

```
words = QuranData.getAyahWords(surah, ayah)  // all words
words = words.filter(isAyahMarker === false)   // exclude markers
norm = words.map(getNormalizedWord)            // strip harakat

for i = 0 to norm.length - 3:
    trigram = norm[i] + " " + norm[i+1] + " " + norm[i+2]
    if hifzData[trigram] exists:
        similar = hifzData[trigram] - [current ayah key]
        if similar not empty:
            → record match at positions [i, i+2]
```

### Step 2 — Merge overlapping matches
Consecutive or overlapping matches are merged into blocks (e.g., matching words at [0,2] and [1,3] → single block [0,3]).

### Step 3 — Render hifz blocks (`_renderHifzWords`)

Uses the **full ayah word list** to build a position→group map, then renders only the line's words while opening/closing `<span class="hifz-block">` tags when entering/leaving a highlighted range.

This approach correctly handles ayahs that span multiple physical page lines — the index mapping uses the global word position (not the line-local position).

### Step 4 — Tooltip on hover

When the user hovers a hifz block:
1. Parse `data-group` JSON (contains matching trigram words + similar ayah keys)
2. For each similar ayah key, fetch its full text from `QuranData.getAyahText()`
3. Highlight the matching words in the tooltip preview
4. Position tooltip below/above the block to stay in viewport
5. On click, `goToAyah()` navigates to the similar ayah's page

---

## Copy preview

### Step 1 — Build preview text (`_copy`)

**Case A — No text selection:**
```
text = QuranData.getAyahText(selectedSurah, selectedAyah)
// e.g., "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ (١)"
```

`getAyahText()` joins all words including the ayah marker (wrapped in parentheses).

**Case B — Text selection active:**
```
1. Find all <span class="word"> that intersect the selection range
2. Group them by their parent .ayah's data-key
3. For each group, look up the imlaei text by data-word
4. Markers are included and wrapped in parentheses
```

### Step 2 — Show preview panel
```
→ renders a floating overlay with the preview text
→ buttons: نسخ, مشاركة, إضافة الآية التالية
```

### Step 3 — "إضافة الآية التالية" button
```
1. Take the last ayah key in _previewKeys
2. Call _getNextAyah(surah, ayah)
   → if ayah < maxAyah: return same surah, ayah+1
   → if surah < 114: return surah+1, ayah 1
   → else: return null (end of Quran)
3. Fetch next ayah text and append with a space separator
```

### Step 4 — "نسخ" button
```
navigator.clipboard.writeText(previewText)
→ hide preview panel
→ show green toast "تم النسخ بنجاح" for 2 seconds
```

### Step 5 — "مشاركة" button
```
navigator.share({ text: previewText })  // Web Share API
→ hide preview panel
```

---

## Key design decisions

**Why each word in its own `<span>`?**
- Enables precise copy: detect exactly which word spans intersect the user's selection
- No complex character-to-word index mapping needed
- Each word has `data-word="N"` for direct imlaei text lookup

**Why sort qpc entries by `id` and not by string key?**
- `Object.keys()` on the JSON returns string-sorted keys ("10:1:1" before "2:1:1")
- The `id` field is sequential (1–83668) and matches the correct Quranic order
- Sorting by `id` ensures words are processed in correct Quran order

**Why group ayahs by the `ayah` field instead of detecting marker text?**
- Each word already has `surah` and `ayah` fields from the source data
- Grouping by the `ayah` field is more reliable than detecting digit markers
- Consistent behavior even if marker format changes

**Why use the full ayah word list for hifz rendering?**
- Hifz `startWord`/`endWord` indices are based on the complete ayah word array
- A page line may contain only a subset of an ayah's words (when ayah spans multiple lines)
- Using the full ayah list avoids out-of-bounds access when indexing the line fragment
