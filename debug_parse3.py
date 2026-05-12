with open('debug_output.txt', 'w', encoding='utf-8') as out:
    with open('mushaf.txt', 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
        out.write(f"Total lines in file: {len(lines)}\n")
        
        for i in range(min(5, len(lines))):
            line = lines[i].strip()
            out.write(f"Line {i+1}: {line[:50]}...\n")
            
            colon_pos = line.find(':')
            if colon_pos > 0:
                before = line[:colon_pos]
                after = line[colon_pos+1:]
                comma_pos = after.find(',')
                out.write(f"  colon_pos={colon_pos}, before='{before}', comma_pos={comma_pos}\n")
                if comma_pos > 0:
                    out.write(f"  rest before comma: '{after[:comma_pos]}'\n")