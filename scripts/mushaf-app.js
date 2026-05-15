// Main app controller: rendering, user interaction, hifz mode, copy preview
class MushafApp {
  constructor() {
    this.data = new QuranData()
    this.currentPage = 1
    this.totalPages = 604
    this.isHifzMode = false
    this.selectedAyahKey = null      // "surah:ayah" key of clicked ayah
    this._tooltipTimer = null
    this._suppressHover = false      // blocks tooltip show during navigation
    this._previewKeys = []           // ayah keys currently in the copy preview
    this._previewText = ''           // accumulated text in the copy preview
  }

  // Entry point: load bismillah font, load all data, build page map, render
  async init() {
    document.getElementById('content').innerHTML = '<span class="loading">جاري التحميل...</span>'

    // Bismillah font = QPC page 1 font (BSML.woff2) with a custom font-family name
    await this._loadFont(1, 'QPC_Bismillah', true)

    await this.data.load()
    this._buildAyahPageMap()

    this._setupEvents()

    this.currentPage = this._getInitialPage()
    await this.renderPage(this.currentPage)
  }

  // Precompute a map: "surah:ayah" -> page number
  // Used by goToAyah() to navigate to the correct page
  _buildAyahPageMap() {
    this.ayahPageMap = new Map()
    for (const [page, lines] of this.data.pageLines) {
      for (const line of lines) {
        if (line.lineType === 'ayah' && line.firstWordId && line.lastWordId) {
          const words = this.data.getWordsInRange(line.firstWordId, line.lastWordId)
          for (const word of words) {
            const key = `${word.surah}:${word.ayah}`
            if (!this.ayahPageMap.has(key)) this.ayahPageMap.set(key, page)
          }
        }
      }
    }
  }

  // Load a QCF font from the woff2 file and inject it as a base64 @font-face
  // Each page has its own font (QCF_P001.woff2 .. QCF_P604.woff2)
  async _loadFont(pageNum, customName, isBismillah = false) {
    const fontName = customName || 'p' + pageNum
    const fontFile = isBismillah ? 'p1.woff2' : 'p' + pageNum + '.woff2'
    const styleId = customName || 'font-' + pageNum
    if (!document.getElementById(styleId)) {
      try {
        const res = await fetch('qpc-fonts/' + fontFile)
        if (res.ok) {
          const buf = await res.arrayBuffer()
          let binary = ''
          const bytes = new Uint8Array(buf)
          for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i])
          }
          const b64 = btoa(binary)
          const style = document.createElement('style')
          style.id = styleId
          style.textContent = `@font-face { font-family: '${fontName}'; src: url(data:font/woff2;base64,${b64}) format('woff2'); }`
          document.head.appendChild(style)
        }
      } catch (e) {
        console.error(`Failed to load font ${fontFile}:`, e)
      }
    }
    try { await document.fonts.load(`100px '${fontName}'`) } catch (e) { }
  }

  // Read initial page from URL hash (#page=N) or default to page 1
  _getInitialPage() {
    const hash = window.location.hash
    if (hash.startsWith('#page=')) {
      const p = parseInt(hash.replace('#page=', ''))
      if (p >= 1 && p <= this.totalPages) return p
    }
    return 1
  }

  // Wire up all DOM event listeners (called once in init)
  _setupEvents() {
    // Navigation buttons
    document.getElementById('firstBtn').onclick = () => this.renderPage(1)
    document.getElementById('prevBtn').onclick = () => this.renderPage(Math.max(1, this.currentPage - 1))
    document.getElementById('nextBtn').onclick = () => this.renderPage(Math.min(this.totalPages, this.currentPage + 1))
    document.getElementById('lastBtn').onclick = () => this.renderPage(this.totalPages)

    // Direct page input
    document.getElementById('pageInput').addEventListener('change', e => {
      const p = parseInt(e.target.value)
      if (p >= 1 && p <= this.totalPages) {
        this.renderPage(p)
      } else {
        e.target.value = this.currentPage
      }
    })

    // Hifz toggle
    document.getElementById('hifzToggle').onclick = () => this._toggleHifz()

    // Copy button — opens the preview panel
    document.getElementById('copyBtn').onclick = () => this._copy()

    // Copy preview panel buttons
    document.getElementById('previewCopyBtn').onclick = () => this._previewCopy()
    document.getElementById('previewShareBtn').onclick = () => this._previewShare()
    document.getElementById('previewNextBtn').onclick = () => this._previewAddNext()
    document.getElementById('previewCloseBtn').onclick = () => this._hideCopyPreview()
    document.getElementById('copyPreview').onclick = e => { if (e.target === e.currentTarget) this._hideCopyPreview() }

    // Info button — opens the info panel
    document.getElementById('infoBtn').onclick = () => this._showInfo()
    document.getElementById('infoCloseBtn').onclick = () => this._hideInfo()
    document.getElementById('infoPreview').onclick = e => { if (e.target === e.currentTarget) this._hideInfo() }

    // Keyboard shortcuts
    document.addEventListener('keydown', e => {
      if (e.target.id === 'pageInput') return
      if (e.key === 'ArrowLeft') this.renderPage(Math.min(this.totalPages, this.currentPage + 1))
      if (e.key === 'ArrowRight') this.renderPage(Math.max(1, this.currentPage - 1))
    })

    // Tap outside the tooltip on mobile closes it immediately
    document.addEventListener('touchstart', e => {
      if (document.getElementById('tooltip').contains(e.target)) return
      this._hideTooltip()
    }, { passive: true })

    // Intercept Ctrl+C / right-click→Copy to copy directly without preview panel
    document.addEventListener('copy', e => {
      const sel = window.getSelection()
      if (sel && !sel.isCollapsed && sel.rangeCount > 0) {
        const range = sel.getRangeAt(0)
        let hasWord = false
        for (const w of document.querySelectorAll('.word')) {
          if (range.intersectsNode(w)) { hasWord = true; break }
        }
        if (!hasWord) return
      } else if (!this.selectedAyahKey) {
        return
      }
      e.preventDefault()
      this._copy(false)
    })

    // Update copy button label based on whether text is selected
    document.addEventListener('selectionchange', () => {
      const sel = window.getSelection()
      const btn = document.getElementById('copyBtn')
      if (sel && !sel.isCollapsed) {
        btn.disabled = false
        btn.textContent = 'نسخ المحدد'
      } else {
        btn.textContent = 'نسخ الآية'
        btn.disabled = !this.selectedAyahKey
      }
    })
  }

  // ─────────────────────────── Page rendering ───────────────────────────

  // Render one mushaf page (1-604) from pages.json into a 15-line grid
  async renderPage(page, onComplete) {
    this._hideTooltip()
    this.selectedAyahKey = null
    document.getElementById('copyBtn').disabled = true
    history.replaceState(null, '', '#page=' + page)
    this.currentPage = page

    const el = document.getElementById('content')
    el.innerHTML = ''

    // Set padding to match quranFrame.png safe area (140/1024 = 13.671875% of padding-box)
    const mushafPage = el.parentElement
    const pageW = mushafPage.clientWidth
    const pad = Math.round(pageW * 0.13671875)
    mushafPage.style.padding = pad + 'px'

    const fontLoad = this._loadFont(page)
    const fontName = 'p' + page
    const lines = this.data.getPageLines(page)

    // Build empty 15-line grid
    let html = ''
    for (let i = 0; i < 15; i++) {
      html += `<div class="page-line" data-line="${i + 1}"></div>`
    }
    el.innerHTML = html
    el.style.fontFamily = `'${fontName}', serif`

    await fontLoad

    // Measure once layout is established
    const containerWidth = el.clientWidth
    const containerHeight = el.clientHeight
    const lineH = containerHeight / 15

    // Calculate and apply optimal font-size
    const fontSize = this._calcFontSize(page, lines, containerWidth)
    if (fontSize) el.style.fontSize = fontSize + 'px'
    for (const child of el.children) {
      child.style.lineHeight = lineH + 'px'
    }

    // Place content into correct line slots
    const isShort = page <= 2
    const offset = isShort ? 3 : 0

    for (const line of lines) {
      const idx = (line.lineNumber - 1) + offset
      if (idx < 0 || idx >= 15) continue
      const slot = el.children[idx]

      if (line.lineType === 'surah_name') {
        const name = this.data.getSurahName(line.surahNumber)
        slot.innerHTML = `<div class="surah-header">سورة ${name}</div>`
        slot.style.textAlign = 'center'
      } else if (line.lineType === 'basmallah') {
        slot.innerHTML = `<span class="bismillah">
          <span class="word" data-text="بِسْمِ">ﭑ</span>
          <span class="word" data-text="اللَّهِ">ﭒ</span>
          <span class="word" data-text="الرَّحْمَٰنِ">ﭓ</span>
          <span class="word" data-text="الرَّحِيمِ">ﭔ</span>
        </span>`
        slot.style.textAlign = 'center'
      } else if (line.lineType === 'ayah' && line.words.length > 0) {
        slot.innerHTML = this._renderAyahLine(line.words)
        slot.style.textAlign = ''
      }
    }

    document.getElementById('pageInput').value = page
    document.getElementById('prevBtn').disabled = page === 1
    document.getElementById('nextBtn').disabled = page === this.totalPages

    if (onComplete) onComplete()
  }

  // Measure all ayah lines at a test size and compute the font-size
  // that makes the widest line fill the container.
  _calcFontSize(page, lines, targetWidth) {
    const testSize = 100
    if (!targetWidth || targetWidth <= 0) return 42
    const measurer = document.createElement('div')
    measurer.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font-size:' + testSize + 'px'
    measurer.style.fontFamily = `'p${page}', serif`
    document.body.appendChild(measurer)
    let maxWidth = 0
    for (const line of lines) {
      if (line.lineType !== 'ayah' || !line.words || line.words.length === 0) continue
      measurer.textContent = line.words.map(w => w.glyph).join('')
      const w = measurer.offsetWidth
      if (w > maxWidth) maxWidth = w
    }
    document.body.removeChild(measurer)
    if (maxWidth === 0) return 42
    return Math.max(10, Math.min(Math.floor(testSize * targetWidth / maxWidth), 200))
  }

  // Split a page line's words by ayah boundaries and render each as an ayah span
  // One physical page line can contain words from multiple ayahs
  _renderAyahLine(words) {
    // Group consecutive words that belong to the same ayah
    const groups = []
    let current = []
    for (const w of words) {
      if (current.length > 0 && current[0].ayah !== w.ayah) {
        groups.push(current)
        current = []
      }
      current.push(w)
    }
    if (current.length > 0) groups.push(current)

    // Render each ayah group as a clickable ayah span
    return groups.map(group => {
      const surah = group[0].surah
      const ayah = group[0].ayah
      const key = `${surah}:${ayah}`
      const hasSimilar = this.isHifzMode && this._checkSimilar(key)

      let innerHtml
      if (this.isHifzMode && hasSimilar) {
        innerHtml = this._renderHifzWords(group, surah, ayah)
      } else {
        // Each word gets its own <span class="word"> for easy selection detection
        innerHtml = group.map(w => `<span class="word" data-word="${w.word}">${w.glyph}</span>`).join('')
      }

      const cls = 'ayah' + (hasSimilar ? ' has-similar' : '')
      return `<span class="${cls}" data-surah="${surah}" data-ayah="${ayah}" data-key="${key}" onclick="app.selectAyah(this)">${innerHtml}</span>`
    }).join('')
  }

  // ─────────────────────────── Ayah selection ───────────────────────────

  // Click handler: highlight all ayah spans sharing the same key
  // (an ayah may span multiple physical lines = multiple .ayah elements)
  selectAyah(el) {
    document.querySelectorAll('.ayah.selected').forEach(a => a.classList.remove('selected'))
    const key = el.dataset.key
    document.querySelectorAll(`.ayah[data-key="${key}"]`).forEach(a => a.classList.add('selected'))
    this.selectedAyahKey = key
    document.getElementById('copyBtn').disabled = false
  }

  // Navigate to the page containing (surah, ayah) and select it
  goToAyah(surah, ayah) {
    const page = this.ayahPageMap.get(`${surah}:${ayah}`)
    if (!page) return
    this._suppressHover = true
    this.renderPage(page, () => {
      const el = document.querySelector(`[data-key="${surah}:${ayah}"]`)
      if (el) this.selectAyah(el)
      setTimeout(() => { this._suppressHover = false }, 200)
    })
  }

  // ─────────────────────────── Copy preview panel ───────────────────────

  // Build the preview text from selected ayah / text selection and show panel
  _copy(showPreview = true) {
    this._previewKeys = []
    let lastSurah = 0, lastAyah = 0

    const sel = window.getSelection()

    if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
      if (!this.selectedAyahKey) return
      const [s, a] = this.selectedAyahKey.split(':').map(Number)
      let text = this.data.getAyahText(s, a)
      if (!text) return

      if (a === 1 && s !== 1 && s !== 9) {
        text = 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ' + text
        this._previewKeys = ['basmallah', this.selectedAyahKey]
      } else {
        this._previewKeys = [this.selectedAyahKey]
      }

      this._previewText = text
      lastSurah = s; lastAyah = a
    } else {
      const range = sel.getRangeAt(0)
      const allWords = document.querySelectorAll('.word')
      const picked = []
      for (const ws of allWords) {
        if (range.intersectsNode(ws)) {
          picked.push(ws)
        }
      }

      if (picked.length === 0) {
        if (!this.selectedAyahKey) return
        const [s, a] = this.selectedAyahKey.split(':').map(Number)
        const text = this.data.getAyahText(s, a)
        if (!text) return
        this._previewKeys = [this.selectedAyahKey]
        this._previewText = text
        lastSurah = s; lastAyah = a
      } else {
        const sequence = []
        for (const ws of picked) {
          const ay = ws.closest('.ayah')
          if (ay) {
            const key = ay.dataset.key
            const wi = parseInt(ws.dataset.word)
            sequence.push({ key, type: 'ayah', value: wi, el: ws })
          } else if (ws.closest('.bismillah')) {
            sequence.push({ key: 'basmallah', type: 'basmallah', value: ws.dataset.text, el: ws })
          }
        }

        const parts = []
        let currentGroup = null

        for (const item of sequence) {
          if (!currentGroup || currentGroup.key !== item.key || currentGroup.type !== item.type) {
            if (currentGroup) {
              if (currentGroup.type === 'ayah') {
                const [s, a] = currentGroup.key.split(':').map(Number)
                const words = this.data.getAyahWords(s, a)
                const pickedWords = words.filter(w => currentGroup.values.includes(w.word))
                parts.push(pickedWords.map(w => this.data.isAyahMarker(w.text) ? `(${w.text})` : w.text).join(' '))
                this._previewKeys.push(currentGroup.key)
                lastSurah = s; lastAyah = a
              } else {
                parts.push(currentGroup.values.join(' '))
                this._previewKeys.push('basmallah')
              }
            }
            currentGroup = { key: item.key, type: item.type, values: [] }
          }
          currentGroup.values.push(item.value)
        }

        if (currentGroup) {
          if (currentGroup.type === 'ayah') {
            const [s, a] = currentGroup.key.split(':').map(Number)
            const words = this.data.getAyahWords(s, a)
            const pickedWords = words.filter(w => currentGroup.values.includes(w.word))
            parts.push(pickedWords.map(w => this.data.isAyahMarker(w.text) ? `(${w.text})` : w.text).join(' '))
            this._previewKeys.push(currentGroup.key)
            lastSurah = s; lastAyah = a
          } else {
            parts.push(currentGroup.values.join(' '))
            this._previewKeys.push('basmallah')
          }
        }

        if (parts.length === 0) return
        this._previewText = parts.join(' ')
      }
    }

    this._previewLastSurah = lastSurah
    this._previewLastAyah = lastAyah

    const isTextSelected = (sel && !sel.isCollapsed && sel.rangeCount > 0);

    if (showPreview && !isTextSelected) {
      this._showCopyPreview()
    } else {
      this._previewCopy()
    }
  }

  // Show the floating preview panel with accumulated text
  _showCopyPreview() {
    document.getElementById('previewText').textContent = this._previewText
    document.getElementById('copyPreview').style.display = 'flex'
  }

  // Hide the preview panel
  _hideCopyPreview() {
    document.getElementById('copyPreview').style.display = 'none'
  }

  // Show the info panel
  _showInfo() {
    document.getElementById('infoPreview').style.display = 'flex'
  }

  // Hide the info panel
  _hideInfo() {
    document.getElementById('infoPreview').style.display = 'none'
  }

  // Copy preview text to clipboard and show success toast
  _previewCopy() {
    navigator.clipboard.writeText(this._previewText)
    this._hideCopyPreview()
    const t = document.getElementById('toast')
    t.style.display = 'block'
    setTimeout(() => { t.style.display = 'none' }, 2000)
  }

  // Share via Web Share API (mobile browsers)
  _previewShare() {
    if (navigator.share) {
      navigator.share({ text: this._previewText })
    }
    this._hideCopyPreview()
  }

  // Append the next consecutive ayah to the preview text
  _previewAddNext() {
    if (this._previewKeys.length === 0) return
    const lastKey = this._previewKeys[this._previewKeys.length - 1]
    let lastSurah, lastAyah
    if (lastKey === 'basmallah') {
      // If the last thing added was a Bismillah, we don't have a specific ayah key to increment
      // but usually, we are at the start of a surah. 
      // However, for this specific logic, we check the range.
      // Since _previewKeys tracks the sequence, if it's just Bismillah, 
      // we might not know the current surah/ayah.
      // But in MushafApp, normally Bismillah is followed by 1:1.
      // For this function, we need the last ayah reference.
      if (!this._previewLastSurah) return
      lastSurah = this._previewLastSurah
      lastAyah = this._previewLastAyah
    } else {
      const [s, a] = lastKey.split(':').map(Number)
      lastSurah = s; lastAyah = a
    }

    const next = this._getNextAyah(lastSurah, lastAyah)
    if (!next) return
    const nextKey = `${next.surah}:${next.ayah}`
    const nextText = this.data.getAyahText(next.surah, next.ayah)
    if (!nextText) return

    let prefix = ' '
    if (next.surah !== lastSurah) {
      if (next.surah === 1 || next.surah === 9) {
        prefix = '\n'
      } else {
        prefix = '\nبِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ '
        this._previewKeys.push('basmallah')
      }
    }

    this._previewKeys.push(nextKey)
    this._previewLastSurah = next.surah
    this._previewLastAyah = next.ayah
    this._previewText += prefix + nextText
    document.getElementById('previewText').textContent = this._previewText
  }

  // Find the next ayah (wraps to next surah at boundaries)
  _getNextAyah(surah, ayah) {
    const max = this.data.getAyahCount(surah)
    if (ayah < max) return { surah, ayah: ayah + 1 }
    if (surah < 114) return { surah: surah + 1, ayah: 1 }
    return null
  }

  // ─────────────────────────── Hifz mode ────────────────────────────────

  // Toggle hifz mode on/off and re-render with highlights
  _toggleHifz() {
    this.isHifzMode = !this.isHifzMode
    document.getElementById('hifzToggle').classList.toggle('active', this.isHifzMode)
    this.renderPage(this.currentPage)
  }

  // Quick check: does this ayah have any matching trigrams?
  _checkSimilar(key) {
    if (!key || !this.isHifzMode) return false
    const [s, a] = key.split(':').map(Number)
    return this._getMatchingGroups(s, a).length > 0
  }

  // Find all trigram matches for an ayah and merge overlapping groups
  // Returns [{startWord, endWord, trigramWordSets, similarAyahs}, ...]
  _getMatchingGroups(surah, ayah) {
    // Get all words for this ayah, filter out markers, normalize
    const words = this.data.getAyahWords(surah, ayah)
      .filter(w => !this.data.isAyahMarker(w.text))
    const norm = words.map(w => this.data.getNormalizedWord(w.text))

    // Find all 3-word sequences that exist in hifz_data.json
    // hifz_data.json keys are normalized trigrams, values are arrays of "surah:ayah"
    const matches = []
    for (let i = 0; i < norm.length - 2; i++) {
      const tri = norm.slice(i, i + 3).join(' ')
      if (this.data.hifzData[tri]) {
        const similar = this.data.hifzData[tri].filter(k => k !== `${surah}:${ayah}`)
        if (similar.length > 0) {
          matches.push({
            startWord: i, endWord: i + 2,
            trigramWords: norm.slice(i, i + 3),
            similarAyahs: similar,
          })
        }
      }
    }
    if (matches.length === 0) return []

    // Merge consecutive or overlapping matches into blocks
    matches.sort((a, b) => a.startWord - b.startWord)
    const merged = []
    let cur = { startWord: matches[0].startWord, endWord: matches[0].endWord, matches: [matches[0]] }
    for (let i = 1; i < matches.length; i++) {
      if (matches[i].startWord <= cur.endWord) {
        cur.endWord = Math.max(cur.endWord, matches[i].endWord)
        cur.matches.push(matches[i])
      } else {
        merged.push(cur)
        cur = { startWord: matches[i].startWord, endWord: matches[i].endWord, matches: [matches[i]] }
      }
    }
    merged.push(cur)

    return merged.map(g => {
      const allSimilar = new Set()
      const sets = g.matches.map(m => ({ words: m.trigramWords, similarAyahs: m.similarAyahs }))
      g.matches.forEach(m => m.similarAyahs.forEach(a => allSimilar.add(a)))
      return { startWord: g.startWord, endWord: g.endWord, trigramWordSets: sets, similarAyahs: [...allSimilar] }
    })
  }

  // Render an ayah's words with hifz blocks around matching trigrams
  // Uses the FULL ayah word list for index mapping (correct across line boundaries)
  _renderHifzWords(lineWords, surah, ayah) {
    const groups = this._getMatchingGroups(surah, ayah)
    if (groups.length === 0) {
      return lineWords.map(w => `<span class="word" data-word="${w.word}">${w.glyph}</span>`).join('')
    }

    // Build a map: word position → hifz group for the full ayah
    const allWords = this.data.getAyahWords(surah, ayah)
    const allNon = allWords.filter(w => !this.data.isAyahMarker(w.text))
    const hl = new Map()
    for (const g of groups) {
      for (let i = g.startWord; i <= g.endWord; i++) {
        if (allNon[i]) hl.set(allNon[i].word, g)
      }
    }

    // Render the current line's words, opening/closing hifz-blocks as needed
    let html = ''
    let block = null
    for (const w of lineWords) {
      if (this.data.isAyahMarker(w.text)) {
        if (block) { html += '</span>'; block = null }
        html += `<span class="word" data-word="${w.word}">${w.glyph}</span>`
      } else if (hl.has(w.word)) {
        const g = hl.get(w.word)
        if (block !== g) {
          if (block) html += '</span>'
          const blockId = `${surah}:${ayah}:${g.startWord}-${g.endWord}`
          const data = JSON.stringify({
            key: `${surah}:${ayah}`,
            startIdx: g.startWord,
            endIdx: g.endWord,
            similarAyahs: g.similarAyahs,
            trigramWordSets: g.trigramWordSets,
          }).replace(/"/g, '&quot;')
          html += `<span class="hifz-block" data-block-id="${blockId}" data-group="${data}" onmouseenter="app._onHifzHover(this)" onmouseleave="app._onHifzLeave()">`
          block = g
        }
        html += `<span class="word" data-word="${w.word}">${w.glyph}</span>`
      } else {
        if (block) { html += '</span>'; block = null }
        html += `<span class="word" data-word="${w.word}">${w.glyph}</span>`
      }
    }
    if (block) html += '</span>'

    return html
  }

  // ─────────────────────────── Tooltip (similar ayahs) ──────────────────

  _onHifzHover(el) {
    if (this._suppressHover) return
    clearTimeout(this._tooltipTimer)
    const blockId = el.dataset.blockId
    if (blockId) {
      document.querySelectorAll(`.hifz-block[data-block-id="${blockId}"]`).forEach(b => b.classList.add('hifz-hovered'))
    }
    this._showTooltip(el)
  }

  _onHifzLeave() {
    document.querySelectorAll('.hifz-hovered').forEach(b => b.classList.remove('hifz-hovered'))
    this._tooltipTimer = setTimeout(() => {
      document.getElementById('tooltip').style.display = 'none'
    }, 800)
  }

  _keepTooltip() {
    clearTimeout(this._tooltipTimer)
  }

  _hideTooltip() {
    clearTimeout(this._tooltipTimer)
    document.querySelectorAll('.hifz-hovered').forEach(b => b.classList.remove('hifz-hovered'))
    document.getElementById('tooltip').style.display = 'none'
  }

  _hideTooltipAfter(ms) {
    this._tooltipTimer = setTimeout(() => {
      document.querySelectorAll('.hifz-hovered').forEach(b => b.classList.remove('hifz-hovered'))
      document.getElementById('tooltip').style.display = 'none'
    }, ms)
  }

  // Build and position the similar-ayahs tooltip
  _showTooltip(el) {
    const raw = el.dataset.group
    if (!raw) return
    const group = JSON.parse(raw)

    // Collect similar ayahs with their matching trigram words highlighted
    const similar = []
    for (const otherKey of group.similarAyahs) {
      const [s, a] = otherKey.split(':').map(Number)
      const text = this.data.getAyahText(s, a)
      const matchingSets = []
      for (const ws of group.trigramWordSets) {
        if (ws.similarAyahs.includes(otherKey)) matchingSets.push(ws.words)
      }
      if (text) {
        similar.push({ key: otherKey, surah: s, ayah: a, text, trigramWordSets: matchingSets })
      }
    }
    if (similar.length === 0) return

    // Render tooltip HTML
    const tooltip = document.getElementById('tooltip')
    let html = `<div class="current-word">آيات مشابهة لهذا الجزء (${similar.length})</div>`
    for (const s of similar) {
      const hl = this._highlightWords(s.text, s.trigramWordSets)
      html += `<div class="similar-item" onclick="app.goToAyah(${s.surah}, ${s.ayah})">
        <div class="surah-name">سورة ${this.data.getSurahName(s.surah)} [${s.surah}:${s.ayah}]</div>
        <div class="ayah-text">${hl}</div>
      </div>`
    }
    tooltip.innerHTML = html

    // Position tooltip below or above the hovered element to avoid overflow
    tooltip.style.display = 'block'
    const h = tooltip.offsetHeight
    tooltip.style.display = 'none'

    const rect = el.getBoundingClientRect()
    const left = rect.left + 15
    const below = window.innerHeight - rect.bottom
    const above = rect.top
    const top = below >= h + 15 ? rect.bottom + 15 : above >= h + 15 ? rect.top - h - 15 : rect.bottom + 15

    tooltip.style.left = left + 'px'
    tooltip.style.top = top + 'px'
    tooltip.style.display = 'block'
    tooltip.onmouseenter = () => this._keepTooltip()
    tooltip.onmouseleave = () => this._hideTooltipAfter(800)
  }

  // Highlight matching words within a similar-ayah preview (tooltip)
  _highlightWords(text, trigramWordSets) {
    if (!trigramWordSets || trigramWordSets.length === 0) return text
    const words = text.split(' ')
    const highlight = new Map()
    const sorted = [...trigramWordSets].sort((a, b) => b.length - a.length)
    for (const set of sorted) {
      for (let i = 0; i < words.length - set.length + 1; i++) {
        const slice = words.slice(i, i + set.length).map(w => this.data.getNormalizedWord(w))
        if (slice.join(' ') === set.join(' ')) {
          for (let j = 0; j < set.length; j++) {
            const pos = i + j
            if (!highlight.has(pos) || set.length > highlight.get(pos)) {
              highlight.set(pos, set.length)
            }
          }
        }
      }
    }
    return words.map((w, i) => highlight.has(i) ? `<span class="hifz-word">${w}</span>` : w).join(' ')
  }
}
