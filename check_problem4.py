# Check actual content of lines around 6099
with open('mushaf.txt', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

with open('debug.txt', 'w', encoding='utf-8') as f:
    for i in [6096, 6097, 6098, 6099, 6100, 6125, 6126, 6127]:
        if i < len(lines):
            line = lines[i].strip()
            f.write(f"Line {i+1}: {line[:50]}...\n")
            
            # Parse surah number
            comma = line.find(',')
            if comma > 0:
                surah = line[:comma]
                f.write(f"  Parsed surah: {surah}\n")