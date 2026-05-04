#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Surah names mapping (1-114)
SURAH_NAMES = {
    1: "سُورَةُ الْفَاتِحَةِ", 2: "سُورَةُ الْبَقَرَةِ", 3: "سُورَةُ آلِ عِمْرَانَ",
    4: "سُورَةُ النِّسَاءِ", 5: "سُورَةُ الْمَائِدَةِ", 6: "سُورَةُ الْأَنْعَامِ",
    7: "سُورَةُ الْأَعْرَافِ", 8: "سُورَةُ الْأَنْفَالِ", 9: "سُورَةُ التَّوْبَةِ",
    10: "سُورَةُ يُونُسَ", 11: "سُورَةُ هُودٍ", 12: "سُورَةُ يُوسُفَ",
    13: "سُورَةُ الرَّعْدِ", 14: "سُورَةُ إِبْرَاهِيمَ", 15: "سُورَةُ الْحِجْرِ",
    16: "سُورَةُ النَّحْلِ", 17: "سُورَةُ الْإِسْرَاءِ", 18: "سُورَةُ الْكَهْفِ",
    19: "سُورَةُ مَرْيَمَ", 20: "سُورَةُ طَهَ", 21: "سُورَةُ الْأَنْبِيَاءِ",
    22: "سُورَةُ الْحَجِّ", 23: "سُورَةُ الْمُؤْمِنِينَ", 24: "سُورَةُ النُّورِ",
    25: "سُورَةُ الْفُرْقَانِ", 26: "سُورَةُ الشُّعَرَاءِ", 27: "سُورَةُ النَّمْلِ",
    28: "سُورَةُ الْقَصَصِ", 29: "سُورَةُ الْعَنْكَبُوتِ", 30: "سُورَةُ الرُّومِ",
    31: "سُورَةُ لُقْمَانَ", 32: "سُورَةُ السَّجْدَةِ", 33: "سُورَةُ الْأَحْزَابِ",
    34: "سُورَةُ سَبَأٍ", 35: "سُورَةُ فَاطِرٍ", 36: "سُورَةُ يُسَعَ",
    37: "سُورَةُ الصَّافَّاتِ", 38: "سُورَةُ صَ", 39: "سُورَةُ الزُّمَرِ",
    40: "سُورَةُ غَافِرٍ", 41: "سُورَةُ فُصِّلَتْ", 42: "سُورَةُ الشُّورَى",
    43: "سُورَةُ الزُّخْرُفِ", 44: "سُورَةُ الدُّخَانِ", 45: "سُورَةُ الْجَاثِيَةِ",
    46: "سُورَةُ الْأَحْقَافِ", 47: "سُورَةُ مُحَمَّدٍ", 48: "سُورَةُ الْفَتْحِ",
    49: "سُورَةُ الْحُجُرَاتِ", 50: "سُورَةُ قَ", 51: "سُورَةُ الذَّارِيَاتِ",
    52: "سُورَةُ الطُّورِ", 53: "سُورَةُ النَّجْمِ", 54: "سُورَةُ الْقَمَرِ",
    55: "سُورَةُ الرَّحْمَنِ", 56: "سُورَةُ الْوَاقِعَةِ", 57: "سُورَةُ الْحَدِيدِ",
    58: "سُورَةُ الْمُجَادِلَةِ", 59: "سُورَةُ الْحَشْرِ", 60: "سُورَةُ الْمُمْتَحَنَةِ",
    61: "سُورَةُ الصَّفِّ", 62: "سُورَةُ الْجُمُعَةِ", 63: "سُورَةُ الْمُنَافِقُونَ",
    64: "سُورَةُ التَّغَابُنِ", 65: "سُورَةُ الطَّلَاقِ", 66: "سُورَةُ التَّحْرِيمِ",
    67: "سُورَةُ الْمُلْكِ", 68: "سُورَةُ الْقَلَمِ", 69: "سُورَةُ الْحَاقَّةِ",
    70: "سُورَةُ الْمَعَارِجِ", 71: "سُورَةُ نُوحٍ", 72: "سُورَةُ الْجِنِّ",
    73: "سُورَةُ الْمُزَّمِّلِ", 74: "سُورَةُ الْمُدَّثِّرِ", 75: "سُورَةُ الْقِيَامَةِ",
    76: "سُورَةُ الْإِنْسَانِ", 77: "سُورَةُ الْمُرْسَلَاتِ", 78: "سُورَةُ النَّبَأِ",
    79: "سُورَةُ النَّازِعَاتِ", 80: "سُورَةُ عَبَسَ", 81: "سُورَةُ التَّكْوِيرِ",
    82: "سُورَةُ الْإِنْفِطَارِ", 83: "سُورَةُ الْمُطَفِّفِينَ", 84: "سُورَةُ الْإِنْشِقَاقِ",
    85: "سُورَةُ الْبُرُوجِ", 86: "سُورَةُ الطَّارِقِ", 87: "سُورَةُ الْأَعْلَى",
    88: "سُورَةُ الْغَاشِيَةِ", 89: "سُورَةُ الْفَجْرِ", 90: "سُورَةُ الْبَلَدِ",
    91: "سُورَةُ الشَّمْسِ", 92: "سُورَةُ اللَّيْلِ", 93: "سُورَةُ الضُّحَى",
    94: "سُورَةُ الشَّرْحِ", 95: "سُورَةُ التِّينِ", 96: "سُورَةُ الْعَلَقِ",
    97: "سُورَةُ الْقَدْرِ", 98: "سُورَةُ الْبَيِّنَةِ", 99: "سُورَةُ الزَّلْزَلَةِ",
    100: "سُورَةُ الْعَادِيَاتِ", 101: "سُورَةُ الْقَارِعَةِ", 102: "سُورَةُ التَّكَاثُرِ",
    103: "سُورَةُ الْعَصْرِ", 104: "سُورَةُ الْهُمَزَةِ", 105: "سُورَةُ الْفِيلِ",
    106: "سُورَةُ قُرَيْشٍ", 107: "سُورَةُ الْمَاعُونَ", 108: "سُورَةُ الْكَوْثَرِ",
    109: "سُورَةُ الْكَافِرُونَ", 110: "سُورَةُ النَّصْرِ", 111: "سُورَةُ الْمَسَدِ",
    112: "سُورَةُ الْإِخْلَاصِ", 113: "سُورَةُ الْفَلَقِ", 114: "سُورَةُ النَّاسِ"
}

# Which verses start each surah (approximate - based on standard Mushaf)
SURAH_START_VERSES = {
    1: 1, 2: 2, 3: 50, 4: 23, 5: 26, 6: 87, 7: 206, 8: 33, 9: 0, 10: 1,
    11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1, 20: 1,
    21: 1, 22: 1, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 29: 1, 30: 1,
    31: 1, 32: 1, 33: 1, 34: 1, 35: 1, 36: 1, 37: 1, 38: 1, 39: 1, 40: 1,
    41: 1, 42: 1, 43: 1, 44: 1, 45: 1, 46: 1, 47: 1, 48: 1, 49: 1, 50: 1,
    51: 1, 52: 1, 53: 1, 54: 1, 55: 1, 56: 1, 57: 1, 58: 1, 59: 1, 60: 1,
    61: 1, 62: 1, 63: 1, 64: 1, 65: 1, 66: 1, 67: 1, 68: 1, 69: 1, 70: 1,
    71: 1, 72: 1, 73: 1, 74: 1, 75: 1, 76: 1, 77: 1, 78: 1, 79: 1, 80: 1,
    81: 1, 82: 1, 83: 1, 84: 1, 85: 1, 86: 1, 87: 1, 88: 1, 89: 1, 90: 1,
    91: 1, 92: 1, 93: 1, 94: 1, 95: 1, 96: 1, 97: 1, 98: 1, 99: 1, 100: 1,
    101: 1, 102: 1, 103: 1, 104: 1, 105: 1, 106: 1, 107: 1, 108: 1, 109: 1, 110: 1,
    111: 1, 112: 1, 113: 1, 114: 1
}

# Page to surah mapping (simplified - main surahs that start on each page)
PAGE_SURAH_START = {
    1: [1], 2: [2], 3: [2], 4: [2], 5: [2], 6: [2], 7: [2], 8: [2], 9: [2], 10: [2],
    11: [2], 12: [2], 13: [3], 14: [3], 15: [3], 16: [3], 17: [3], 18: [3], 19: [3], 20: [3],
    21: [3], 22: [4], 23: [4], 24: [4], 25: [4], 26: [4], 27: [4], 28: [4], 29: [4], 30: [5],
    31: [5], 32: [6], 33: [6], 34: [7], 35: [7], 36: [8], 37: [9], 38: [10], 39: [11], 40: [12],
    41: [13], 42: [14], 43: [15], 44: [16], 45: [17], 46: [18], 47: [19], 48: [20], 49: [21], 50: [22],
    51: [23], 52: [24], 53: [25], 54: [26], 55: [27], 56: [28], 57: [29], 58: [30], 59: [31], 60: [32],
    61: [33], 62: [33], 63: [34], 64: [35], 65: [36], 66: [37], 67: [38], 68: [39], 69: [40], 70: [41],
    71: [42], 72: [43], 73: [44], 74: [45], 75: [46], 76: [47], 77: [48], 78: [49], 79: [50], 80: [51],
    81: [52], 82: [53], 83: [54], 84: [55], 85: [56], 86: [57], 87: [58], 88: [59], 89: [60], 90: [61],
    91: [62], 92: [63], 93: [64], 94: [65], 95: [66], 96: [67], 97: [68], 98: [69], 99: [70], 100: [71],
    101: [72], 102: [73], 103: [74], 104: [75], 105: [76], 106: [77], 107: [78], 108: [79], 109: [80], 110: [81],
    111: [82], 112: [83], 113: [84], 114: [85], 115: [86], 116: [87], 117: [88], 118: [89], 119: [90], 120: [91],
    121: [92], 122: [93], 123: [94], 124: [95], 125: [96], 126: [97], 127: [98], 128: [99], 129: [100], 130: [101],
    131: [102], 132: [103], 133: [104], 134: [105], 135: [106], 136: [107], 137: [108], 138: [109], 139: [110], 140: [111],
    141: [112], 142: [113], 143: [114]
}

FONTS_DIR = "qcf_fonts"
fonts_cache = {}

print("Loading QCF fonts into memory...")
for i in range(1, 605):
    page_num = str(i).zfill(3)
    filepath = os.path.join(FONTS_DIR, f"QCF_P{page_num}.woff2")
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            fonts_cache[page_num] = base64.b64encode(f.read()).decode('utf-8')

print(f"Loaded {len(fonts_cache)} fonts")

page_content = {}
with open('mushaf.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        comma_idx = line.find(',')
        if comma_idx == -1:
            continue
        page_num = line[:comma_idx].strip()
        if page_num not in page_content:
            page_content[page_num] = ""
        page_content[page_num] += line[comma_idx+1:].strip()

print(f"Loaded content for {len(page_content)} pages")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>مصحف المدينة المنورة - صفحة {page_num}</title>
<style>
{fonts_css}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: #c9b896;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  font-family: 'Traditional Arabic', serif;
}}
.nav {{
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  justify-content: center;
}}
.nav button {{
  padding: 10px 20px;
  font-size: 16px;
  background: #8b7748;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
}}
.nav button:hover {{
  background: #6d5a36;
}}
.nav button:disabled {{
  background: #ccc;
  cursor: not-allowed;
}}
.page-info {{
  font-size: 18px;
  color: #8b7748;
  font-weight: bold;
  padding: 0 10px;
}}
.surah-header {{
  text-align: center;
  font-size: 32px;
  color: #8b7748;
  margin: 10px 0 25px 0;
  letter-spacing: 2px;
}}
.mushaf-page {{
  background: linear-gradient(145deg, #fefcf5, #f7f2e3);
  width: 560px;
  min-height: 820px;
  padding: 50px 45px;
  box-shadow: 0 15px 50px rgba(0,0,0,0.3);
  border: 4px double #8b7748;
  position: relative;
}}
.mushaf-page::before {{
  content: '';
  position: absolute;
  top: 24px; left: 24px; right: 24px; bottom: 24px;
  border: 1px solid #8b7748;
  pointer-events: none;
}}
.surah-separator {{
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
  position: relative;
}}
.surah-separator::before, .surah-separator::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, #8b7748, transparent);
}}
.separator-symbol {{
  padding: 0 15px;
  color: #8b7748;
  font-size: 20px;
}}
.qcf-text {{
  font-family: 'QCF_P{page_num}', serif;
  font-size: 52px;
  line-height: 1.35;
  color: #000;
  word-wrap: break-word;
}}
.verse-block {{
  margin: 8px 0;
}}
.page-num {{
  position: absolute;
  bottom: 38px;
  left: 0; right: 0;
  text-align: center;
  font-size: 22px;
  color: #8b7748;
}}
</style>
</head>
<body>
<div class="nav">
  <button onclick="goToPage(1)" {prev_disabled}>« الأولى</button>
  <button onclick="goToPage({page_num} - 1)" {prev_disabled}>‹ السابق</button>
  <span class="page-info">صفحة {page_num_display} / 604</span>
  <button onclick="goToPage({page_num} + 1)" {next_disabled}>التالي ›</button>
  <button onclick="goToPage(604)" {next_disabled}>الأخيرة »</button>
</div>
<div class="mushaf-page">
  {surah_header}
  <div class="qcf-text">{page_text}</div>
  <div class="page-num">{page_num_display}</div>
</div>
<script>
function goToPage(p) {{
  if (p < 1 || p > 604) return;
  window.location.href = '/page/' + p;
}}
document.addEventListener('keydown', function(e) {{
  if (e.key === 'ArrowLeft') goToPage({page_num} - 1);
  if (e.key === 'ArrowRight') goToPage({page_num} + 1);
}});
</script>
</body>
</html>"""

class QuranHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.rstrip('/')
        
        if path == '' or path == '/':
            self.send_response(302)
            self.send_header('Location', '/page/1')
            self.end_headers()
            return
        
        if path.startswith('/page/'):
            try:
                page_num = int(path.split('/')[-1])
                if page_num < 1 or page_num > 604:
                    page_num = 1
            except:
                page_num = 1
            
            page_str = str(page_num).zfill(3)
            
            fonts_css = ""
            for p in range(max(1, page_num-2), min(605, page_num+3)):
                p_str = str(p).zfill(3)
                if p_str in fonts_cache:
                    fonts_css += f"""@font-face {{
  font-family: 'QCF_P{p}';
  src: url(data:font/woff2;base64,{fonts_cache[p_str]}) format('woff2');
}}\n"""
            
            page_text = page_content.get(str(page_num), "")
            
            # Get surah name for header
            surah_header = ""
            if page_num in PAGE_SURAH_START:
                surah_num = PAGE_SURAH_START[page_num]
                if surah_num in SURAH_NAMES:
                    surah_header = f'<div class="surah-header">{SURAH_NAMES[surah_num]}</div>'
            
            # Add surah separator if this page has multiple surahs
            # (simplified: show decorative separator on some pages)
            if page_num > 1 and page_num % 2 == 0:
                page_text = f'<div class="surah-separator"><span class="separator-symbol">﴿</span></div>' + page_text
            
            page_num_display = "١" if page_num == 1 else str(page_num)
            
            prev_disabled = "disabled" if page_num == 1 else ""
            next_disabled = "disabled" if page_num == 604 else ""
            
            html = HTML_TEMPLATE.format(
                page_num=page_num,
                page_num_display=page_num_display,
                fonts_css=fonts_css,
                page_text=page_text,
                surah_header=surah_header,
                prev_disabled=prev_disabled,
                next_disabled=next_disabled
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(html.encode('utf-8')))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            return
        
        super().do_GET()

print("\n=== Starting Enhanced Quran Server ===")
print("Server: http://192.168.1.13:8080")
print("Features: Surah headers, separators, keyboard navigation")

server = HTTPServer(('0.0.0.0', 8080), QuranHandler)
server.serve_forever()