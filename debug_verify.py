import json
import re

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('mushaf.txt', 'r', encoding='utf-8-sig') as f:
    mushaf_lines = [line.strip() for line in f]

# Build all_ayahs
all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

# Test the exact function from verify_mapping.py
def get_word_count_from_text(text, remove_basmala=True):
    words = [w for w in re.split(r'\s+', text.strip()) if w]
    if remove_basmala and len(words) >= 4:
        if words[0].startswith('ب') and words[1] == 'ٱللَّهِ' and words[2] == 'ٱلرَّحْمَٰنِ':
            words = words[4:]
    return words

# Check lines 6099 and 6126
with open('debug.txt', 'w', encoding='utf-8') as f:
    for line_num in [6099, 6126]:
        idx = line_num - 1
        
        # Get Quran words
        quran_ayah = all_ayahs[idx]
        quran_words = get_word_count_from_text(quran_ayah['text'])
        
        # Get mushaf chars
        mushaf_line = mushaf_lines[idx]
        comma_pos = mushaf_line.find(',')
        if comma_pos > 0:
            ligatures = mushaf_line[comma_pos+1:]
            mushaf_chars = ligatures[:-1] if ligatures else ''
        
        f.write(f"\nLine {line_num}:\n")
        f.write(f"  Quran words: {len(quran_words)}\n")
        f.write(f"  First 10 words: {quran_words[:10]}\n")
        f.write(f"  Mushaf chars: {len(mushaf_chars)}\n")
        f.write(f"  Match: {len(quran_words) == len(mushaf_chars)}\n")

print("Done")