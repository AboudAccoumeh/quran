import json

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get all surahs
surahs = data['data']['surahs']

# Show first and last surah info
with open('debug.txt', 'w', encoding='utf-8') as f:
    # First surah
    f.write(f"Surah 1 (Al-Fatiha): {len(surahs[0]['ayahs'])} ayahs\n")
    for i, a in enumerate(surahs[0]['ayahs'][:3]):
        f.write(f"  Ayah {a['number']} (in surah {a['numberInSurah']}): {a['text'][:20]}...\n")
    
    # Last surah
    last_surah = surahs[-1]
    f.write(f"\nSurah {last_surah['number']} ({last_surah['englishName']}): {len(last_surah['ayahs'])} ayahs\n")
    for a in last_surah['ayahs']:
        f.write(f"  Ayah {a['number']} (in surah {a['numberInSurah']}): {a['text'][:20]}...\n")
    
    # Total
    total = sum(len(s['ayahs']) for s in surahs)
    f.write(f"\nTotal ayahs: {total}\n")
    
    # Find which surah contains ayah 6099
    count = 0
    for s in surahs:
        for a in s['ayahs']:
            count += 1
            if a['number'] == 6099:
                f.write(f"\nAyah 6099 is in Surah {s['number']}, position {a['numberInSurah']}\n")
                f.write(f"  Text: {a['text'][:50]}...\n")

print("Done")