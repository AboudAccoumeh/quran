import json

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

# Check the problematic lines
for line_num in [6099, 6126]:
    ayah = all_ayahs[line_num - 1]
    words = [w for w in ayah['text'].split() if w]
    with open('debug.txt', 'a', encoding='utf-8') as f:
        f.write(f"\nLine {line_num} (Quran ayah {ayah['number']}):\n")
        f.write(f"  Surah {ayah['numberInSurah']} of {len([s for s in data['data']['surahs'] if s['number'] == (all_ayahs[line_num-2]['number'] if line_num > 1 else 0)])} surahs\n")
        f.write(f"  Word count: {len(words)}\n")
        f.write(f"  Words: {words}\n")

# Also check surah numbers for the +1 cases
for line_num in [86, 188, 1166, 5331]:
    ayah = all_ayahs[line_num - 1]
    with open('debug.txt', 'a', encoding='utf-8') as f:
        f.write(f"\nLine {line_num}: Surah {ayah['numberInSurah']}, Ayah {ayah['number']}\n")

print("Done - check debug.txt")