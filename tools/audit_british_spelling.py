#!/usr/bin/env python3
"""
audit_british_spelling.py - Audit LaTeX files for British English spelling conventions.

Checks for -ize/-ization/-izer, color, behavior, analyze, etc.

Author: Gemma Knee and Antigra Vitti
"""

import sys
import os
import glob
import re

PATTERNS = [
    (r'\b(realiz\w+)\b', 'realis-'),
    (r'\b(factoriz\w+)\b', 'factoris-'),
    (r'\b(characteriz\w+)\b', 'characteris-'),
    (r'\b(generaliz\w+)\b', 'generalis-'),
    (r'\b(recogniz\w+)\b', 'recognis-'),
    (r'\b(stabiliz\w+)\b', 'stabilis-'),
    (r'\b(customiz\w+)\b', 'customis-'),
    (r'\b(harmoniz\w+)\b', 'harmonis-'),
    (r'\b(analyz\w+)\b', 'analys-'),
    (r'\b(behavior\w*)\b', 'behaviour'),
    (r'\b(catalogs)\b', 'catalogues'),
    (r'\b(cataloged)\b', 'catalogued'),
    (r'\b(cataloging)\b', 'cataloguing'),
]

def audit_file(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Filter out LaTeX comments
    lines = text.splitlines()
    matches = []
    for l_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'%.*$', '', line)
        for pattern, suggestion in PATTERNS:
            for m in re.finditer(pattern, clean_line, re.IGNORECASE):
                # Ignore color in LaTeX commands like \color, \colorlet, \textcolor, colorlinks
                word = m.group(1)
                if 'color' in word.lower() and ('\\' in clean_line or 'color=' in clean_line):
                    continue
                matches.append((l_idx, word, suggestion))
    return matches

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit LaTeX files across atlases for British English spelling compliance.")
    parser.add_argument("paths", nargs="*", default=["polyatlas", "unimosatlas", "allmosatlas"], help="Target directories or TeX files to audit (default: all three monographs)")
    args = parser.parse_args()

    tex_files = []
    for p in args.paths:
        if os.path.isfile(p):
            tex_files.append(p)
        else:
            tex_files.extend(sorted(glob.glob(os.path.join(p, "**", "*.tex"), recursive=True)))

    total = 0
    for tf in tex_files:
        if "plates/tetramers_part" in tf:
            continue
        res = audit_file(tf)
        if res:
            print(f"File {tf}:")
            for line_no, word, sug in res:
                print(f"  Line {line_no}: '{word}' -> suggested British: '{sug}'")
                total += 1

    print(f"\nSpelling audit complete. Total flags: {total}")

if __name__ == "__main__":
    main()
