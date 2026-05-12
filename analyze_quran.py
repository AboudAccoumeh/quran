import json

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Analyze unique characters in a sample ayah
sample = data['data']['surahs'][0]['ayahs'][0]['text']
chars = sorted(set(sample))

with open('analysis.txt', 'w', encoding='utf-8') as out:
    out.write("Sample ayahs:\n")
    for surah in data['data']['surahs'][:2]:
        for ayah in surah['ayahs'][:2]:
            out.write(f"Surah {surah['number']}:{ayah['numberInSurah']} -> {ayah['text']}\n")
    
    out.write("\n\nUnique chars in first ayah:\n")
    out.write(str(chars))
    
    out.write("\n\nTotal surahs: " + str(len(data['data']['surahs'])))
    
    # Count total ayahs
    total = sum(len(s['ayahs']) for s in data['data']['surahs'])
    out.write(f"\nTotal ayahs: {total}")

print("Done - check analysis.txt")