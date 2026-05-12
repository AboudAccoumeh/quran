import json

# Load mushaf to see surah numbers
mushaf_data = {}
with open('mushaf.txt', 'r', encoding='utf-8-sig') as f:
    for idx, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        comma_pos = line.find(',')
        if comma_pos > 0:
            surah_num = int(line[:comma_pos])
            mushaf_data[idx] = surah_num

# Check the problematic lines
with open('debug.txt', 'w', encoding='utf-8') as f:
    for line_num in [6099, 6126]:
        surah = mushaf_data.get(line_num, 'N/A')
        f.write(f"Line {line_num}: Mushaf surah = {surah}\n")

# Also show line around 6098-6100
with open('debug.txt', 'a', encoding='utf-8') as f:
    f.write("\n--- Lines around 6099 ---\n")
    for i in range(6096, 6103):
        f.write(f"Line {i}: surah={mushaf_data.get(i, 'N/A')}\n")

print("Done")