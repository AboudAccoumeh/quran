#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.request
import time

fonts_dir = "qcf_fonts"
os.makedirs(fonts_dir, exist_ok=True)

base_url = "https://raw.githubusercontent.com/nuqayah/qpc-fonts/master/mushaf-woff2/QCF_P"

# Count existing
existing = len([f for f in os.listdir(fonts_dir) if f.endswith('.woff2')])
print(f"Already downloaded: {existing} fonts")

failed = []
success_count = existing

print("Continuing download of 604 QCF page fonts...")
start_time = time.time()

for i in range(1, 605):
    page_num = str(i).zfill(3)
    filename = f"QCF_P{page_num}.woff2"
    filepath = os.path.join(fonts_dir, filename)
    url = f"{base_url}{page_num}.woff2"
    
    if os.path.exists(filepath):
        continue
    
    try:
        urllib.request.urlretrieve(url, filepath)
        success_count += 1
        
        # Progress every 25 pages
        if i % 25 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (604 - i) / rate if rate > 0 else 0
            print(f"Progress: {i}/604 ({i*100//604}%) - {success_count} files - ~{remaining:.0f}s remaining")
            
    except Exception as e:
        failed.append((i, str(e)))
    
    if i % 10 == 0:
        time.sleep(0.05)

elapsed_total = time.time() - start_time
print(f"\n=== Download Complete ===")
print(f"Total: {success_count}/604 fonts")
print(f"Time: {elapsed_total:.1f} seconds")
print(f"Size: {sum(os.path.getsize(os.path.join(fonts_dir, f)) for f in os.listdir(fonts_dir) if f.endswith('.woff2')) / 1024 / 1024:.2f} MB")

if failed:
    print(f"Failed: {len(failed)}")
    with open('download_errors.txt', 'w') as f:
        for page, error in failed:
            f.write(f"{page}: {error}\n")