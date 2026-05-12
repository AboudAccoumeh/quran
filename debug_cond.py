import json
import re

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

# Debug the exact condition
with open('debug.txt', 'w', encoding='utf-8') as f:
    idx = 6098
    text = all_ayahs[idx]['text']
    words = [w for w in re.split(r'\s+', text.strip()) if w]
    
    f.write(f"Words: {words[:6]}\n")
    f.write(f"words[0]: '{words[0]}'\n")
    f.write(f"words[0].startswith('ب'): {words[0].startswith('ب')}\n")
    f.write(f"words[1]: '{words[1]}'\n")
    f.write(f"words[1] == 'ٱللَّهِ': {words[1] == 'ٱللَّهِ'}\n")
    f.write(f"words[2]: '{words[2]}'\n")
    f.write(f"words[2] == 'ٱلرَّحْمَٰنِ': {words[2] == 'ٱلرَّحْمَٰنِ'}\n")
    
    # Check condition result
    cond = words[0].startswith('ب') and words[1] == 'ٱللَّهِ' and words[2] == 'ٱلرَّحْمَٰنِ'
    f.write(f"\nCondition result: {cond}\n")
    
    # Show full condition breakdown
    f.write(f"\nBreakdown:\n")
    f.write(f"  1: {words[0].startswith('ب')}\n")
    f.write(f"  2: {words[1] == 'ٱللَّهِ'}\n")
    f.write(f"  3: {words[2] == 'ٱلرَّحْمَٰنِ'}\n")

print("Done")