import json

mushaf_data = {}
with open('mushaf.txt', 'r', encoding='utf-8-sig') as f:
    lines_read = 0
    loaded = 0
    for line in f:
        lines_read += 1
        line = line.strip()
        if not line:
            continue
        colon_pos = line.find(':')
        if colon_pos > 0:
            try:
                line_num = int(line[:colon_pos].strip())
                rest = line[colon_pos+1:].strip()
                comma_idx = rest.find(',')
                if comma_idx > 0:
                    surah_num = int(rest[:comma_idx].strip())
                    ligatures = rest[comma_idx+1:]
                    mushaf_data[line_num] = {'surah': surah_num, 'ligatures': ligatures, 'len': len(ligatures)}
                    loaded += 1
                    if loaded <= 5:
                        # Write to file instead of printing
                        with open('debug_output.txt', 'a', encoding='utf-8') as out:
                            out.write(f"Line {line_num}: surah={surah_num}, lig_len={len(ligatures)}\n")
            except Exception as e:
                pass

with open('debug_output.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total lines: {lines_read}, Loaded: {len(mushaf_data)}\n")
    for k in list(mushaf_data.keys())[:10]:
        out.write(f"Key {k}: {mushaf_data[k]}\n")

print("Done - check debug_output.txt")