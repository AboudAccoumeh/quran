import json
import re

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

with open('debug.txt', 'w', encoding='utf-8') as f:
    for idx in [6098]:
        ayah = all_ayahs[idx]
        words = [w for w in re.split(r'\s+', ayah['text'].strip()) if w]
        
        first = words[0]
        f.write(f"First word: {first}\n")
        f.write(f"Repr: {repr(first)}\n")
        f.write(f"Length: {len(first)}\n")
        
        # Check each character
        f.write(f"Chars: ")
        for c in first:
            f.write(f"U+{ord(c):04X} ")
        f.write("\n")
        
        # Simple check - does word start with ب ?
        f.write(f"Starts with ب: {first.startswith('ب')}\n")
        f.write(f"'ب' in first: {'ب' in first}\n")

print("Done")