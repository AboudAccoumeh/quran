import json

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find surahs 597 and 598
for surah in data['data']['surahs']:
    if surah['number'] in [97, 98]:
        print(f"Surah {surah['number']}: {surah['englishName']} - {len(surah['ayahs'])} ayahs")

# Find ayahs 6099 and 6126
all_ayahs = []
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        all_ayahs.append(ayah)

print(f"\nAyah 6099: Surah {all_ayahs[6098]['numberInSurah']}, global {all_ayahs[6098]['number']}")
print(f"  Text: {all_ayahs[6098]['text']}")

print(f"\nAyah 6126: Surah {all_ayahs[6125]['numberInSurah']}, global {all_ayahs[6125]['number']}")
print(f"  Text: {all_ayahs[6125]['text']}")