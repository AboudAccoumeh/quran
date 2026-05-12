import json

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

# Lines 6099 and 6126 in mushaf = Quran ayahs 6099 and 6126 (0-indexed)
with open('debug.txt', 'w', encoding='utf-8') as f:
    for idx in [6098, 6125]:  # 0-indexed
        ayah = all_ayahs[idx]
        words = [w for w in ayah['text'].split() if w]
        f.write(f"\nMushaf line {idx+1} = Quran ayah {ayah['number']}:\n")
        f.write(f"  Surah {ayah['numberInSurah']}, Juz {ayah['juz']}\n")
        f.write(f"  Word count: {len(words)}\n")
        f.write(f"  Words: {words[:10]}...\n")

# Also check for the +1 cases
for idx in [85, 187, 1165, 5330]:
    if idx < len(all_ayahs):
        ayah = all_ayahs[idx]
        words = [w for w in ayah['text'].split() if w]
        with open('debug.txt', 'a', encoding='utf-8') as f:
            f.write(f"\nLine {idx+1} = Quran ayah {ayah['number']}:\n")
            f.write(f"  Surah {ayah['numberInSurah']}, word count: {len(words)}\n")

print("Done")