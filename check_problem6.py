import json

with open('quran-uthmani.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build ayah lookup properly
ayah_by_number = {}
for surah in data['data']['surahs']:
    for ayah in surah['ayahs']:
        ayah_by_number[ayah['number']] = ayah

# Check the problematic ones
with open('debug.txt', 'w', encoding='utf-8') as f:
    for ayah_num in [6099, 6126]:
        ayah = ayah_by_number.get(ayah_num)
        if ayah:
            words = [w for w in ayah['text'].split() if w]
            f.write(f"\nQuran ayah {ayah_num}:\n")
            f.write(f"  Surah {ayah['numberInSurah']},ayah {ayah['numberInSurah']}, global {ayah['number']}\n")
            f.write(f"  Word count: {len(words)}\n")
            f.write(f"  Text: {words}\n")
    
    # Verify by checking a known ayah
    f.write(f"\n--- Verification ---\n")
    f.write(f"Total ayahs: {len(ayah_by_number)}\n")
    f.write(f"First ayah: Surah {ayah_by_number[1]['numberInSurah']}, text: {ayah_by_number[1]['text'][:30]}\n")
    f.write(f"Last ayah: Surah {ayah_by_number[6236]['numberInSurah']}, text: {ayah_by_number[6236]['text'][:30]}\n")

print("Done")