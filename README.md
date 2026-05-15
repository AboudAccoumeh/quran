# Quran Mushaf — مصحف المدينة المنورة

A fully offline-capable digital Mushaf web application that renders the Holy Quran using authentic QCF (Quranic Calligraphy Font) glyphs, replicating the Madani Mushaf page layout.

## Features

- **Authentic rendering** — Each of the 604 pages uses the official QCF v1 font for accurate Quranic script
- **Page navigation** — Next/Previous, First/Last buttons + direct page input + URL hash linking (`#page=N`)
- **Verse selection & copy** — Click a verse to select it, or highlight specific words; copy with preview panel
- **Share verses** — Web Share API integration for sharing verse text
- **Hifz (memorization) mode** — Toggle highlight mode that detects trigram overlaps between verses; hover to see similar ayahs and navigate to them
- **Add consecutive verses** — Chain multiple verses together in the copy preview
- **Persistent hifz data** — Trigram similarity data built from the full Quran text
- **Fully client-side** — No server needed; works from any static file server or even local file:// (CORS permitting)

## Tech Stack

- HTML5 + CSS3 (vanilla)
- JavaScript (ES6+) — no frameworks, no dependencies
- QCF v1 woff2 fonts (from [Qul / Tarteel](https://qul.tarteel.ai/resources))
- Python 3 (data processing utility)

## Project Structure

```
quran-mushaf/
├── index.html                # Entry point (RTL Arabic)
├── styles/styles.css         # All styling
├── scripts/
│   ├── quran-data.js         # Data loading & query layer
│   └── mushaf-app.js         # App controller, rendering, interactions
├── data/
│   ├── pages.json            # Page layout (line types, word ID ranges)
│   ├── qpc-v1-glyph-codes-wbw.json  # Word-by-word QCF glyph codes
│   ├── imlaei.json           # Word-by-word readable Arabic text
│   ├── surah_info.json       # Surah names
│   └── hifz_data.json        # Trigram → similar ayahs lookup
├── qcf_fonts/                # QCF_P001.woff2 … QCF_P604.woff2
├── images/
│   ├── quranFrame.png
│   └── SurahHeader.png
├── utility/
│   └── build_hifz_data.py    # Builds hifz_data.json from imlaei.json
├── WORKFLOW.md               # Detailed rendering workflow documentation
└── README.md
```

## Getting Started

```bash
# Serve locally (any HTTP server works)
python -m http.server 8000
# or
npx serve .
```

Then open `http://localhost:8000` in a modern browser.

You can also open `index.html` directly if your browser allows `file://` access to local fonts (some browsers may block this).

## How it works

1. **Data loading** — 5 JSON files (glyph codes, imlaei text, page layout, surah info, hifz data) load in parallel
2. **Font loading** — QCF `.woff2` fonts are fetched per-page, converted to base64, and injected as `@font-face` rules
3. **Page rendering** — Each page is built from word-by-word glyph spans grouped by ayah, with surah headers and basmallah lines
4. **Hifz mode** — Trigram matching identifies similar verses; overlapping matches merge into highlight blocks with hover tooltips

## Hifz Data Build

```bash
python utility/build_hifz_data.py
```

Processes `imlaei.json` to generate trigram similarity data written to `data/hifz_data.json`.

## Browser Support

Modern browsers with ES6+ support, CSS `@font-face`, and `fetch` + `ArrayBuffer` support.

## Acknowledgements

- Quran text data and QCF fonts sourced from [Qul / Tarteel](https://qul.tarteel.ai/resources)
- Inspired by the Madani Mushaf layout

## License

MIT
