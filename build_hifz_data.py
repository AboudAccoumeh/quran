import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HARAKAT = ['ً', 'ٍ', 'ٌ', 'َ', 'ِ', 'ُ', 'ّ', 'ْ', 'ٰ', 'ٱ']

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

BISMILLAH = data['data']['surahs'][0]['ayahs'][0]['text'].replace('\ufeff', '').strip()

def normalize(w):
    for h in HARAKAT:
        w = w.replace(h, '')
    return w.strip()

def remove_bismillah(text):
    text = text.replace('\ufeff', '').strip()
    if text.startswith(BISMILLAH):
        remaining = text[len(BISMILLAH):].strip()
        if len(remaining) <= 5:
            return ""
        return remaining
    return text

def get_trigrams(text):
    """Extract trigrams (3 consecutive words) from text"""
    text = text.strip()
    if not text:
        return []
    words = text.split(' ')
    trigrams = []
    for i in range(len(words) - 2):
        w1 = normalize(words[i])
        w2 = normalize(words[i + 1])
        w3 = normalize(words[i + 2])
        if w1 and w2 and w3:
            trigrams.append(w1 + " " + w2 + " " + w3)
    return trigrams

print("Building trigram index...")
trigram_to_ayahs = {}

for surah in data['data']['surahs']:
    surahNum = surah['number']
    for ayah in surah['ayahs']:
        ayahNum = ayah['numberInSurah']
        key = f"{surahNum}:{ayahNum}"
        
        text = remove_bismillah(ayah['text'])
        if not text:
            continue
            
        trigrams = get_trigrams(text)
        for trigram in trigrams:
            if trigram not in trigram_to_ayahs:
                trigram_to_ayahs[trigram] = []
            trigram_to_ayahs[trigram].append(key)

print(f"Total unique trigrams: {len(trigram_to_ayahs)}")

# Filter: keep only trigrams appearing 2+ times
similarTrigrams = {k: v for k, v in trigram_to_ayahs.items() if len(v) >= 2}
print(f"Similar trigrams (2+ occurrences): {len(similarTrigrams)}")

# Remove bismillah-related entries
bismillah_words = ['بسم', 'لله', 'لرحمن', 'لرحيم']
filtered = {}
for key, ayahs in similarTrigrams.items():
    is_bismillah = any(bw in key for bw in bismillah_words)
    if not is_bismillah:
        filtered[key] = ayahs

print(f"After bismillah filter: {len(filtered)}")

# Save result
with open('hifz_data.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, ensure_ascii=False)

print("Saved to hifz_data.json")

# Show some examples
samples = list(filtered.items())[:5]
for k, v in samples:
    print(f"  {k}: {v}")