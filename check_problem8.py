import json

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build flat list
all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

# Check specific problematic lines
with open('debug.txt', 'w', encoding='utf-8') as f:
    # Line 6099 = index 6098, Line 6126 = index 6125
    for idx in [6098, 6125]:
        ayah = all_ayahs[idx]
        words = [w for w in ayah['text'].split() if w]
        
        # Remove basmala if present
        if len(words) >= 4 and words[0] == 'بِسْمِ':
            words_no_basmala = words[4:]
        else:
            words_no_basmala = words
        
        f.write(f"\nLine {idx+1}:\n")
        f.write(f"  Global ayah: {ayah['number']}\n")
        f.write(f"  Words with basmala: {len(words)}\n")
        f.write(f"  Words without basmala: {len(words_no_basmala)}\n")
        f.write(f"  First 10 words: {words_no_basmala[:10]}\n")

print("Done")