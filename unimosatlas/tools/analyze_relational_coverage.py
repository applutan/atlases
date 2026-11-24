#!/usr/bin/env python3
"""
analyze_relational_coverage.py - Inspect composition coverage across mosaic blocks.

Analyzes how the blocks of composition mosaics in Z_4, Z_9, and Z_16 inject into
the canonical composition census of polyatlas (inngons.tsv):
  - Inscribed polygon class coverage (which classes appear, which are absent)
  - Frequency distribution of polygon classes across mosaics
  - Direct (+) vs retrograde (-) enantiomorphic distribution

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import argparse
from collections import Counter

def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze polygon composition class coverage in mosaic blocks."
    )
    parser.add_argument(
        "--blocks-tsv",
        type=str,
        required=True,
        help="Path to mosaic blocks TSV (e.g. unimosatlas/data/z16_mosaic_blocks.tsv)"
    )
    parser.add_argument(
        "--inngons-tsv",
        type=str,
        default="polyatlas/data/inngons.tsv",
        help="Path to polyatlas inngons.tsv"
    )
    parser.add_argument(
        "--target-n",
        type=int,
        required=True,
        help="Cyclic lattice order n (e.g. 4, 9, 16)"
    )
    parser.add_argument(
        "--target-k",
        type=int,
        required=True,
        help="Target block size k (e.g. 2 for Z_4, 3 for Z_9, 4 for Z_16)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    print("=" * 70)
    print(f"COMPOSITION COVERAGE ANALYSIS: Z_{args.target_n} (k={args.target_k})")
    print("=" * 70)

    # 1. Load available classes from inngons.tsv
    all_classes = {}
    with open(args.inngons_tsv, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            comp, class_id, n_str, k_str, subset, orb_sz, is_achiral = parts[:7]
            if n_str.isdigit() and int(n_str) == args.target_n and k_str.isdigit() and int(k_str) == args.target_k:
                all_classes[class_id] = {
                    "composition": comp,
                    "subset": subset,
                    "is_achiral": bool(int(is_achiral)),
                    "orbit_size": int(orb_sz)
                }

    print(f"Total canonical classes of {args.target_k}-gons in Z_{args.target_n}: {len(all_classes)}")

    # 2. Count occurrences in mosaic blocks TSV
    class_counts = Counter()
    chirality_counts = Counter()
    total_blocks = 0

    with open(args.blocks_tsv, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            # Look for poly_class column:
            # Header has: ... poly_class canon_comp realised_comp root chirality ...
            # In z16_mosaic_blocks: idx 7 is poly_class, idx 11 is chirality
            # In z8_mosaic_blocks: idx 5 is poly_class, idx 9 is chirality
            # Let's inspect dynamically
            if line.startswith("orbit_id"):
                headers = parts
                c_idx = headers.index("poly_class")
                ch_idx = headers.index("chirality")
                continue
            
            p_class = parts[c_idx]
            ch_sign = parts[ch_idx]
            class_counts[p_class] += 1
            chirality_counts[(p_class, ch_sign)] += 1
            total_blocks += 1

    present_classes = set(class_counts.keys())
    missing_classes = set(all_classes.keys()) - present_classes

    print(f"Total mosaic block records analyzed: {total_blocks:,}")
    print(f"Classes appearing in mosaics:         {len(present_classes)} / {len(all_classes)} ({len(present_classes)/len(all_classes)*100:.1f}%)")
    print(f"Classes absent from mosaics:          {len(missing_classes)}")

    if missing_classes:
        print("\nAbsent classes (unrealised in equal-block partition mosaics):")
        for mc in sorted(missing_classes, key=lambda c: int(c.split("-")[1])):
            info = all_classes[mc]
            achir = "achiral" if info["is_achiral"] else "chiral"
            print(f"  {mc:<6s} strides: {info['composition']:<6s} ({achir}) subset: {info['subset']}")
    else:
        print("\nAll canonical composition classes are realised (surjective block embedding)!")

    print("\nTop 10 Most Frequent Polygon Classes in Mosaics:")
    for p_class, cnt in class_counts.most_common(10):
        info = all_classes.get(p_class, {})
        achir = "achiral" if info.get("is_achiral", False) else "chiral"
        plus_cnt = chirality_counts.get((p_class, "+"), 0)
        minus_cnt = chirality_counts.get((p_class, "-"), 0)
        pct = cnt / total_blocks * 100
        print(f"  {p_class:<6s} (strides {info.get('composition','?'):<5s}, {achir:<7s}): {cnt:7,d} blocks ({pct:5.2f}%) [+: {plus_cnt:,}, -: {minus_cnt:,}]")

    print("=" * 70)

if __name__ == "__main__":
    main()
