import json
import re
from collections import defaultdict

HARAKAT = ['ً', 'ٍ', 'ٌ', 'َ', 'ِ', 'ُ', 'ّ', 'ْ', 'ٰ']
STOP_MARKS = ['ۖ', 'ۗ', 'ۘ', 'ۙ', 'ۚ', 'ۛ']

with open('data/imlaei.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def normalize(w):
    for h in HARAKAT:
        w = w.replace(h, '')
    for m in STOP_MARKS:
        w = w.replace(m, '')
    return w.strip()

def is_ayah_marker(text):
    return all(c in '٠١٢٣٤٥٦٧٨٩' for c in text.strip())

def get_trigrams(text):
    text = text.strip()
    if not text:
        return []
    for m in STOP_MARKS:
        text = text.replace(m, '')
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split(' ')
    trigrams = []
    for i in range(len(words) - 2):
        w1 = normalize(words[i])
        w2 = normalize(words[i + 1])
        w3 = normalize(words[i + 2])
        if w1 and w2 and w3:
            trigrams.append(f"{w1} {w2} {w3}")
    return trigrams

print("Grouping words by ayah...")
ayah_groups = defaultdict(list)

for key, entry in data.items():
    text = entry['text']
    if is_ayah_marker(text):
        continue
    ak = f"{entry['surah']}:{entry['ayah']}"
    ayah_groups[ak].append((int(entry['word']), text))

print("Building trigram index...")
trigram_to_ayahs = defaultdict(list)

for ak, words in ayah_groups.items():
    words.sort(key=lambda x: x[0])
    ayah_text = ' '.join(w[1] for w in words)
    trigrams = get_trigrams(ayah_text)
    for trigram in trigrams:
        trigram_to_ayahs[trigram].append(ak)

print(f"Total unique trigrams: {len(trigram_to_ayahs)}")

# Filter: keep only trigrams appearing 2+ times
similarTrigrams = {k: v for k, v in trigram_to_ayahs.items() if len(v) >= 2}
print(f"Similar trigrams (2+ occurrences): {len(similarTrigrams)}")

# Remove bismillah-related entries
bismillah_words = ['بسم', 'لله', 'لرحمن', 'لرحيم']
filtered = {}
for key, ayahs in similarTrigrams.items():
    if not any(bw in key for bw in bismillah_words):
        filtered[key] = ayahs

print(f"After bismillah filter: {len(filtered)}")

with open('data/hifz_data.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, ensure_ascii=False)

print("Saved to data/hifz_data.json")

samples = list(filtered.items())[:5]
for k, v in samples:
    print(f"  {k}: {v}")
