mushaf_data = {}
with open('mushaf.txt', 'r', encoding='utf-8-sig') as f:
    lines_read = 0
    loaded = 0
    for line in f:
        lines_read += 1
        line = line.strip()
        if not line:
            continue
        
        # Detailed debug
        colon_pos = line.find(':')
        if colon_pos > 0:
            before_colon = line[:colon_pos]
            after_colon = line[colon_pos+1:]
            
            # Check if after colon has comma
            comma_pos = after_colon.find(',')
            
            # Write debug info
            with open('debug_output.txt', 'a', encoding='utf-8') as out:
                out.write(f"Line {lines_read}: colon_pos={colon_pos}, before='{before_colon}', after_len={len(after_colon)}, comma_pos={comma_pos}\n")
                if lines_read <= 3:
                    out.write(f"  first 20 of after_colon: {after_colon[:20]}\n")
                    out.write(f"  rest[:comma]={after_colon[:comma_pos] if comma_pos > 0 else 'N/A'}\n")

with open('debug_output.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total: {lines_read}\n")