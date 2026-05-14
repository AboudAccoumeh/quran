// Data layer: loads all JSON sources and provides query methods
// Two word-by-word files (qpc + imlaei) share the same key "surah:ayah:word"
// and are linked by sequential id for correct order.
class QuranData {
  constructor() {
    this.wordsById = new Map()        // id -> {surah, ayah, word, glyph, text}
    this.ayahWords = new Map()        // "surah:ayah" -> [words including markers]
    this.ayahWordsNoMarker = new Map() // "surah:ayah" -> [words excluding markers]
    this.surahNames = {}              // surahNumber -> {name, ...} from surah_info.json
    this.pageLines = new Map()        // page -> [{lineType, firstWordId, lastWordId, ...}]
    this.hifzData = {}                // normalized trigram -> [surah:ayah keys]
  }

  // Fetch all 5 JSON files in parallel, build word maps and page structure
  async load() {
    const [qpcRaw, imlRaw, pagesRaw, surahInfo, hifzRaw] = await Promise.all([
      fetch('data/qpc-v1-glyph-codes-wbw.json').then(r => r.json()),
      fetch('data/imlaei.json').then(r => r.json()),
      fetch('data/pages.json').then(r => r.json()),
      fetch('data/surah_info.json').then(r => r.json()),
      fetch('data/hifz_data.json').then(r => r.json()),
    ])

    this.surahNames = surahInfo
    this.hifzData = hifzRaw

    // Sort ALL word entries by their sequential id (not by string key)
    // This is critical — Object.keys() returns string-sorted order
    // which would place "10:1:1" before "2:1:1"
    const entries = Object.entries(qpcRaw)
      .map(([k, v]) => ({ key: k, val: v }))
      .sort((a, b) => a.val.id - b.val.id)

    // Build word lookup maps from both files (same key structure)
    for (const { key, val: q } of entries) {
      const im = imlRaw[key]
      const w = {
        id: q.id,
        surah: parseInt(q.surah),
        ayah: parseInt(q.ayah),
        word: parseInt(q.word),
        glyph: q.text,   // special glyph character rendered via QCF font
        text: im.text,   // readable Arabic text for copy/display
      }
      this.wordsById.set(q.id, w)

      const ak = `${w.surah}:${w.ayah}`
      if (!this.ayahWords.has(ak)) this.ayahWords.set(ak, [])
      this.ayahWords.get(ak).push(w)

      if (!this.isAyahMarker(w.text)) {
        if (!this.ayahWordsNoMarker.has(ak)) this.ayahWordsNoMarker.set(ak, [])
        this.ayahWordsNoMarker.get(ak).push(w)
      }
    }

    // Ensure words within each ayah are ordered by word position
    for (const [, words] of this.ayahWords) words.sort((a, b) => a.word - b.word)
    for (const [, words] of this.ayahWordsNoMarker) words.sort((a, b) => a.word - b.word)

    // Parse pages.json into page -> lines structure
    // Each line has a type: surah_name, basmallah, or ayah (with word id range)
    for (const entry of pagesRaw) {
      const page = entry.page_number
      if (!this.pageLines.has(page)) this.pageLines.set(page, [])
      this.pageLines.get(page).push({
        lineNumber: entry.line_number,
        lineType: entry.line_type,
        firstWordId: entry.first_word_id,
        lastWordId: entry.last_word_id,
        surahNumber: entry.surah_number || null,
        isCentered: entry.is_centered,
      })
    }
  }

  // Look up surah name from surah_info.json
  getSurahName(surahNumber) {
    const info = this.surahNames[surahNumber]
    return info ? info.name : ''
  }

  // Fetch all words whose id falls between firstId and lastId (inclusive)
  // Used to resolve a page line's word range into actual word objects
  getWordsInRange(firstId, lastId) {
    const words = []
    for (let id = firstId; id <= lastId; id++) {
      const w = this.wordsById.get(id)
      if (w) words.push(w)
    }
    return words
  }

  // Ayah markers are Hindu-Arabic digits like ١, ٢, etc.
  isAyahMarker(text) {
    return /^[\d٠-٩]+$/.test(text)
  }

  // For a given page, return all lines with their word objects populated
  getPageLines(page) {
    const lines = this.pageLines.get(page) || []
    return lines.map(line => {
      if (line.lineType === 'ayah' && line.firstWordId && line.lastWordId) {
        return { ...line, words: this.getWordsInRange(line.firstWordId, line.lastWordId) }
      }
      return { ...line, words: [] }
    })
  }

  // All words of an ayah (including markers)
  getAyahWords(surah, ayah) {
    return this.ayahWords.get(`${surah}:${ayah}`) || []
  }

  // Readable text for copy — markers wrapped in parentheses
  getAyahText(surah, ayah) {
    const words = this.ayahWords.get(`${surah}:${ayah}`)
    if (!words) return ''
    return words.map(w => this.isAyahMarker(w.text) ? `(${w.text})` : w.text).join(' ')
  }

  // Glyph string for visual display (concatenated without markers)
  getAyahGlyphs(surah, ayah) {
    const words = this.ayahWords.get(`${surah}:${ayah}`)
    return words ? words.map(w => w.glyph).join('') : ''
  }

  // Total number of ayahs in a surah
  getAyahCount(surah) {
    let max = 0
    for (const [, w] of this.wordsById) {
      if (w.surah === surah && w.ayah > max) max = w.ayah
    }
    return max
  }

  // Single word lookup by its sequential id
  getWordById(id) {
    return this.wordsById.get(id)
  }

  // Strip Arabic diacritics (harakat) for trigram matching
  getNormalizedWord(text) {
    const harakat = ['ً', 'ٍ', 'ٌ', 'َ', 'ِ', 'ُ', 'ّ', 'ْ', 'ٰ']
    let w = text.trim()
    for (const h of harakat) w = w.replaceAll(h, '')
    return w
  }
}
