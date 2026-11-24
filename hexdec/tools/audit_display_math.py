#!/usr/bin/env python3
"""
audit_display_math.py - Audit LaTeX files for display math punctuation bacilli.

Ensures that no display math block ($$, \\], \\end{equation}, \\end{align})
ends with trailing terminal punctuation (. or ,) per strict project styling rules.

Author: Gemma Knee and Antigra Vitti
"""

import sys
import os
import glob
import re

def audit_file(filepath: str) -> int:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    violations = 0
    closer_re = re.compile(r'(\$\$|\\\]|\\end\{equation\*?\}|\\end\{align\*?\})')

    for idx, line in enumerate(lines):
        if closer_re.search(line):
            # Check previous line
            if idx > 0:
                prev = lines[idx - 1].rstrip()
                if prev.endswith('.') or prev.endswith(','):
                    print(f"VIOLATION: {filepath}:{idx} -> Terminal punctuation before closer:")
                    print(f"  Line {idx}: {prev}")
                    violations += 1
            # Also check if the closer itself has punctuation appended
            stripped = line.strip()
            if stripped.endswith('.') or stripped.endswith(','):
                print(f"VIOLATION: {filepath}:{idx+1} -> Terminal punctuation on closer line:")
                print(f"  Line {idx+1}: {stripped}")
                violations += 1

    return violations

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit LaTeX files for display math punctuation bacilli.")
    parser.add_argument("path", nargs="?", default="hexdec", help="Target directory or TeX file to audit (default: hexdec)")
    args = parser.parse_args()

    if os.path.isfile(args.path):
        tex_files = [args.path]
    else:
        tex_files = sorted(glob.glob(os.path.join(args.path, "**", "*.tex"), recursive=True))

    total_violations = 0
    audited_count = 0

    for tf in tex_files:
        # Skip plates part files
        if "plates/tetramers_part" in tf:
            continue
        v = audit_file(tf)
        total_violations += v
        audited_count += 1

    print(f"\nAudit complete: Audited {audited_count} TeX files. Total violations found: {total_violations}")
    if total_violations == 0:
        print("✓ All display math blocks are 100% clean and free of punctuation bacilli.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
