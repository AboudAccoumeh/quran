const http = require('http');
const fs = require('fs');
const path = require('path');

console.log('Loading QCF fonts...');

const FONTS_DIR = path.join(__dirname, 'qcf_fonts');
const fontsCache = {};

for (let i = 1; i <= 604; i++) {
    const pageNum = String(i).padStart(3, '0');
    const filepath = path.join(FONTS_DIR, 'QCF_P' + pageNum + '.woff2');
    if (fs.existsSync(filepath)) {
        const buffer = fs.readFileSync(filepath);
        fontsCache[pageNum] = buffer.toString('base64');
    }
}
console.log('Loaded ' + Object.keys(fontsCache).length + ' fonts');

console.log('Loading mushaf content...');
const mushafContent = {};
const mushafData = fs.readFileSync('mushaf.txt', 'utf-8');
const lines = mushafData.split('\n');
for (let line of lines) {
    if (!line.trim()) continue;
    const commaIdx = line.indexOf(',');
    if (commaIdx === -1) continue;
    const pageNum = line.substring(0, commaIdx).trim();
    const ligatures = line.substring(commaIdx + 1).trim();
    if (!mushafContent[pageNum]) mushafContent[pageNum] = '';
    mushafContent[pageNum] += ligatures;
}
console.log('Loaded content for ' + Object.keys(mushafContent).length + ' pages');

// Simple HTML - just the QCF font rendering - NO manual headers
const HTML_TEMPLATE = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>مصحف المدينة المنورة - صفحة {page}</title>
<style>
{fonts}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #c9b896; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 20px; }
.nav { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.nav button { padding: 10px 20px; font-size: 16px; background: #8b7748; color: white; border: none; border-radius: 8px; cursor: pointer; }
.nav button:hover { background: #6d5a36; }
.nav button:disabled { background: #ccc; cursor: not-allowed; }
.page-info { font-size: 18px; color: #8b7748; font-weight: bold; }
.mushaf-page { background: linear-gradient(145deg, #fefcf5, #f7f2e3); width: 560px; min-height: 820px; padding: 50px 45px; box-shadow: 0 15px 50px rgba(0,0,0,0.3); border: 4px double #8b7748; position: relative; }
.mushaf-page::before { content: ''; position: absolute; top: 24px; left: 24px; right: 24px; bottom: 24px; border: 1px solid #8b7748; pointer-events: none; }
.qcf-text { font-family: 'QCF_P{page}', serif; font-size: 52px; line-height: 1.35; color: #000; word-wrap: break-word; text-align: justify; }
.page-num { position: absolute; bottom: 38px; left: 0; right: 0; text-align: center; font-size: 22px; color: #8b7748; }
</style>
</head>
<body>
<div class="nav">
  <button onclick="location.href='/page/1'">« الأولى</button>
  <button onclick="location.href='/page/{prev}'" {prev_disabled}>‹ السابق</button>
  <span class="page-info">صفحة {page} / 604</span>
  <button onclick="location.href='/page/{next}'" {next_disabled}>التالي ›</button>
  <button onclick="location.href='/page/604'">الأخيرة »</button>
</div>
<div class="mushaf-page">
  <div class="qcf-text">{content}</div>
  <div class="page-num">{page}</div>
</div>
<script>
document.addEventListener('keydown', e => {
  if(e.key === 'ArrowLeft') location.href = '/page/{prev}';
  if(e.key === 'ArrowRight') location.href = '/page/{next}';
});
</script>
</body>
</html>`;

const server = http.createServer((req, res) => {
    const url = (req.url.split('?')[0] || '/').replace(/\/$/, '');
    
    if (url === '' || url === '/') {
        res.writeHead(302, { Location: '/page/1' });
        res.end();
        return;
    }
    
    if (url.startsWith('/page/')) {
        let page = parseInt(url.split('/')[2]) || 1;
        if (page < 1) page = 1;
        if (page > 604) page = 604;
        
        const pageStr = String(page).padStart(3, '0');
        
        // Load font for current page ONLY
        let fontsCSS = '';
        if (fontsCache[pageStr]) {
            fontsCSS = '@font-face { font-family: \'QCF_P' + page + '\'; src: url(data:font/woff2;base64,' + fontsCache[pageStr] + ') format(\'woff2\'); }';
        }
        
        // Content - the QCF ligatures contain EVERYTHING including surah names, separators, etc.
        const content = mushafContent[String(page)] || '';
        
        const prev = Math.max(1, page - 1);
        const next = Math.min(604, page + 1);
        const prevDisabled = page === 1 ? 'disabled' : '';
        const nextDisabled = page === 604 ? 'disabled' : '';
        
        let html = HTML_TEMPLATE
            .replace(/{page}/g, page)
            .replace('{prev}', prev)
            .replace('{next}', next)
            .replace('{fonts}', fontsCSS)
            .replace('{content}', content)
            .replace('{prev_disabled}', prevDisabled)
            .replace('{next_disabled}', nextDisabled);
        
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(html);
        return;
    }
    
    res.writeHead(404);
    res.end('Not Found');
});

server.listen(8080, '0.0.0.0', () => {
    console.log('\n=== Quran Server Running ===');
    console.log('Go to: http://192.168.1.13:8080/page/1');
    console.log('Surah headers are rendered by QCF font - exactly like real Mushaf\n');
});