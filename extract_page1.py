#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('mushaf.txt', 'r', encoding='utf-8') as f:
    content = f.read()

page1_chars = []
lines = content.strip().split('\n')

# Format: "page,ligatures" 
# Example: "1, ligatures"
for line in lines:
    comma_idx = line.find(',')
    
    if comma_idx != -1:
        page_num = line[:comma_idx].strip()
        ligatures = line[comma_idx+1:].strip()
        
        if page_num == '1':
            page1_chars.append(ligatures)

result = ''.join(page1_chars)

with open('page1_ligatures.txt', 'w', encoding='utf-8') as f:
    f.write(result)

with open('extract_log.txt', 'w', encoding='utf-8') as f:
    f.write(f'Found {len(page1_chars)} lines for page 1\n')
    f.write(f'Total characters: {len(result)}\n')
    if len(result) > 0:
        f.write(f'Chars: {len(result)}\n')