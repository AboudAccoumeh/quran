import json
import re

def load_quran_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_mushaf(filepath):
    mushaf_data = {}
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        line_idx = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            line_idx += 1
            # Format: "surah_num,ligatures" - e.g., "1,ﭑﭒﭓﭔﭕ"
            # The line number (1-indexed) is the position in file
            comma_pos = line.find(',')
            if comma_pos > 0:
                try:
                    surah_num = int(line[:comma_pos])
                    ligatures = line[comma_pos+1:]
                    # Remove last char (ayah number) from ligatures
                    actual_chars = ligatures[:-1] if ligatures else ''
                    mushaf_data[line_idx] = {'surah': surah_num, 'ligatures': actual_chars}
                except Exception as e:
                    pass
    print(f"Mushaf: Processed {line_idx} lines, loaded {len(mushaf_data)} entries")
    return mushaf_data

def get_word_count_from_text(text, remove_basmala=True):
    # Split by regex to handle multiple spaces
    words = [w for w in re.split(r'\s+', text.strip()) if w]
    
    # Remove basmala if present (first 4 words: بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ)
    # Simple check: does first word start with ب and second word is ٱللَّهِ ?
    if remove_basmala and len(words) >= 4:
        if words[0].startswith('ب') and words[1] == 'ٱللَّهِ' and words[2] == 'ٱلرَّحْمَٰنِ':
            words = words[4:]
    
    return words

# Stop marks identified by user
STOP_MARKS = [
    'ۖ',  # Line 86
]

def verify_mapping(quran_data, mushaf_data):
    results = []
    errors = []
    
    # Build flat list of all ayahs
    all_ayahs = []
    for surah in quran_data['data']['surahs']:
        for ayah in surah['ayahs']:
            all_ayahs.append(ayah)
    
    # Process each mushaf line
    for line_num, mushaf_line in mushaf_data.items():
        if line_num > len(all_ayahs):
            continue
            
        quran_ayah = all_ayahs[line_num - 1]
        mushaf_text = mushaf_line['ligatures']
        
        # Note: last char already removed in load_mushaf
        # Count "words" in mushaf (each character is a word or stop mark)
        mushaf_word_count = len(mushaf_text)
        
        # Get words from quran json
        quran_words = get_word_count_from_text(quran_ayah['text'])
        quran_word_count = len(quran_words)
        
        # Check if they match
        match = mushaf_word_count == quran_word_count
        
        result = {
            'line': line_num,
            'surah': mushaf_line['surah'],
            'quran_ayah_num': quran_ayah['number'],
            'quran_text': quran_ayah['text'],
            'mushaf_chars': mushaf_text,
            'mushaf_count': mushaf_word_count,
            'quran_count': quran_word_count,
            'match': match
        }
        results.append(result)
        
        if not match:
            errors.append(result)
    
    return results, errors

def print_results(results, errors, output_file='mapping_results.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MAPPING VERIFICATION RESULTS\n")
        f.write("=" * 80 + "\n")
        
        f.write(f"\nTotal lines processed: {len(results)}\n")
        f.write(f"Matching: {sum(1 for r in results if r['match'])}\n")
        f.write(f"Non-matching: {len(errors)}\n")
        
        matching = [r for r in results if r['match']]
        f.write(f"\nMatching lines: {len(matching)}\n")
        for m in matching[:10]:
            f.write(f"  Line {m['line']}: mushaf={m['mushaf_count']} chars, quran={m['quran_count']} words\n")
        
        # Show first few non-matching
        f.write(f"\nFirst 10 non-matching lines:\n")
        for err in errors[:10]:
            f.write(f"  Line {err['line']} (Quran {err['quran_ayah_num']}): mushaf={err['mushaf_count']}, quran={err['quran_count']}\n")
        
        # Analyze mismatch patterns
        f.write("\n" + "=" * 80 + "\n")
        f.write("MISMATCH ANALYSIS:\n")
        f.write("=" * 80 + "\n")
        
        more_in_mushaf = sum(1 for e in errors if e['mushaf_count'] > e['quran_count'])
        more_in_quran = sum(1 for e in errors if e['mushaf_count'] < e['quran_count'])
        equal = sum(1 for e in errors if e['mushaf_count'] == e['quran_count'])
        
        f.write(f"Mushaf has MORE chars than Quran words: {more_in_mushaf}\n")
        f.write(f"Quran has MORE words than Mushaf chars: {more_in_quran}\n")
        f.write(f"Equal but still not matching (stop marks?): {equal}\n")
        
        # Detailed analysis of non-matching
        f.write("\n" + "=" * 80 + "\n")
        f.write("DETAILED NON-MATCHING ANALYSIS:\n")
        f.write("=" * 80 + "\n")
        for err in errors:
            f.write(f"\nLine {err['line']} (Quran {err['quran_ayah_num']}, Surah {err['surah']}):\n")
            f.write(f"  Mushaf: {err['mushaf_count']} chars, Quran: {err['quran_count']} words\n")
            f.write(f"  Diff: {err['mushaf_count'] - err['quran_count']}\n")
    
    print(f"Results written to {output_file}")

def analyze_word_by_word_mapping(quran_data, mushaf_data, output_file='word_mapping.txt'):
    all_ayahs = []
    for surah in quran_data['data']['surahs']:
        for ayah in surah['ayahs']:
            all_ayahs.append(ayah)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("DETAILED WORD-BY-WORD MAPPING (First 10 ayahs)\n")
        f.write("=" * 60 + "\n")
        
        for line_num in range(1, 11):
            if line_num > len(all_ayahs):
                break
                
            mushaf_line = mushaf_data[line_num]
            quran_ayah = all_ayahs[line_num - 1]
            
            # Note: ligatures already have last char removed in load_mushaf
            mushaf_chars = mushaf_line['ligatures']
            quran_words = get_word_count_from_text(quran_ayah['text'])
            
            match = "MATCH" if len(mushaf_chars) == len(quran_words) else "DIFF"
            
            f.write(f"\n--- Line {line_num} (Quran Ayah {quran_ayah['number']}) [{match}] ---\n")
            f.write(f"Quran words ({len(quran_words)}): {quran_words}\n")
            f.write(f"Mushaf chars ({len(mushaf_chars)}): {mushaf_chars[:30]}...\n")
    
    print(f"Word mapping written to {output_file}")

if __name__ == '__main__':
    # Load data
    print("Loading data...")
    quran_data = load_quran_json('quran-uthmani.json')
    mushaf_data = load_mushaf('mushaf.txt')
    
    print(f"Loaded {len(mushaf_data)} mushaf lines")
    total_ayahs = sum(len(s['ayahs']) for s in quran_data['data']['surahs'])
    print(f"Total Quran ayahs: {total_ayahs}")
    
    # Verify mapping
    results, errors = verify_mapping(quran_data, mushaf_data)
    print_results(results, errors)
    
    # Show detailed mapping
    analyze_word_by_word_mapping(quran_data, mushaf_data)