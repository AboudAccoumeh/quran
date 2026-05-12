import json
import re

file_path = r"C:\Users\ABOUD\Desktop\QuranApp\quran-uthmani.json"

# Use utf-8-sig to handle the Byte Order Mark (BOM) mentioned in the error
with open(file_path, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Use a very flexible regex: match "بِسْمِ" at the start, followed by 3 words,
# and ends with "الرَّحِيمِ" or "ٱلرَّحِيمِ". This avoids strict character matching.
bismillah_pattern = re.compile(r'^بِسْمِ\s+[^ ]+\s+[^ ]+\s+[ٱا]لرَّحِيمِ\s*', re.UNICODE)

count = 0
for surah in data['data']['surahs']:
    if surah['number'] != 1 and surah['number'] != 9:
        first_ayah = surah['ayahs'][0]
        text = first_ayah['text']
        
        if bismillah_pattern.match(text):
            first_ayah['text'] = bismillah_pattern.sub('', text).strip()
            count += 1

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Successfully processed {count} surahs.")
