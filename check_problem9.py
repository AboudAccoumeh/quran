import json

# Load mushaf
mushaf_data = {}
with open('mushaf.txt', 'r', encoding='utf-8-sig') as f:
    for idx, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        comma_pos = line.find(',')
        if comma_pos > 0:
            ligatures = line[comma_pos+1:]
            # Remove last char (ayah number)
            actual_chars = ligatures[:-1] if ligatures else ''
            mushaf_data[idx] = actual_chars

# Load Quran
with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

with open('debug.txt', 'w', encoding='utf-8') as f:
    # Line 6099 and 6126
    for line_num in [6099, 6126]:
        mushaf_chars = mushaf_data.get(line_num, '')
        quran_ayah = all_ayahs[line_num - 1]
        
        # Get words (with basmala check)
        words = [w for w in quran_ayah['text'].split() if w]
        
        # Try removing basmala - check for variations
        if len(words) >= 4 and 'ب' in words[0]:
            # Remove first 4 words (basmala)
            words = words[4:]
        
        f.write(f"\nLine {line_num}:\n")
        f.write(f"  Mushaf chars: {len(mushaf_chars)} - '{mushaf_chars[:30]}...'\n")
        f.write(f"  Quran words (after basmala): {len(words)}\n")
        f.write(f"  Quran text: {quran_ayah['text'][:50]}...\n")

# Also check the +1 cases
with open('debug.txt', 'a', encoding='utf-8') as f:
    f.write("\n--- +1 cases (likely stop marks) ---\n")
    for line_num in [86, 188, 1166, 5331]:
        mushaf_chars = mushaf_data.get(line_num, '')
        quran_ayah = all_ayahs[line_num - 1]
        words = [w for w in quran_ayah['text'].split() if w]
        
        if len(words) >= 4 and 'ب' in words[0]:
            words = words[4:]
        
        f.write(f"\nLine {line_num}: mushaf={len(mushaf_chars)}, quran={len(words)}\n")

print("Done")