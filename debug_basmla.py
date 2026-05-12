import json
import re

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

# Debug lines 6099 and 6126
with open('debug.txt', 'w', encoding='utf-8') as f:
    for idx in [6098, 6125]:  # 0-indexed
        ayah = all_ayahs[idx]
        text = ayah['text']
        
        # Split using regex
        words = [w for w in re.split(r'\s+', text.strip()) if w]
        
        f.write(f"\nLine {idx+1} (Ayah {ayah['number']}):\n")
        f.write(f"  Total words: {len(words)}\n")
        f.write(f"  First 10 words: {words[:10]}\n")
        
        # Check basmala
        if len(words) >= 4:
            first_word = words[0]
            f.write(f"  First word check: '{first_word}' contains 'ب': {'ب' in first_word}\n")
            f.write(f"  Contains 'بِسْمِ': {'بِسْمِ' in first_word}\n")
            f.write(f"  Contains 'بِّسْمِ': {'بِّسْمِ' in first_word}\n")

print("Done")