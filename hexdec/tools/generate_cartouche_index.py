#!/usr/bin/env python3
"""
generate_cartouche_index.py - Generate Canonical Partition-Slash Index with Chirality Signatures and Full Cycle Relabelings

Outputs hexdec/data/hexadecality_index.txt with:
- Canonical Cartouche IDs: M01..M14 (Monomers), D001..D295 (Dimers), T00001..T20721 (Tetramers)
- Dihedral orbit sizes |O|, symmetric block counts s, chord dispersion energies E
- Full Galois cycle relabelings: mu_1 -> mu_3 (-> mu_7 -> mu_5)
- Explicit block-by-block chirality signatures: [ssss], [ssnn], [nnnn] for every mosaic in the cycle.

Author: Gemma Knee
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import find_fixed_point_orbits
from hexdec.tools.inspect_first_tetramers import extract_high_symmetry_tetramers, format_partition_slash
from hexdec.tools.generate_dimers_plates import load_and_sort_dimers
from hexdec.tools.mosaic_sorting import (
    get_mosaic_sort_key,
    is_block_symmetric,
    compute_mosaic_chord_energy,
    get_chirality_signature,
)

def generate_index(output_file: str):
    lines = []
    lines.append("# ==============================================================================")
    lines.append("# HEXADECALITY: COMPOSITION MOSAICS ON Z_16 (z_4^4)")
    lines.append("# CANONICAL AFFINE MACRO-ORBIT DIRECTORY & PARTITION INDEX")
    lines.append("#")
    lines.append("# Oligomer Nomenclature:")
    lines.append("#   Monomers  (1-Cycles under mu_3): M01 .. M14 (14 orbits)")
    lines.append("#   Dimers    (2-Cycles under mu_3): D001 .. D295 (590 orbits)")
    lines.append("#   Tetramers (4-Cycles under mu_3): T00001 .. T20721 (82,884 orbits)")
    lines.append("#")
    lines.append("# Partition Format:")
    lines.append("#   Single hexadecimal digits 0..9, A..F for vertices 0..15 on Z_16.")
    lines.append("#   Blocks delimited by slashes: /B0/B1/B2/B3/ in canonical block order.")
    lines.append("#")
    lines.append("# Chirality Signature [c0 c1 c2 c3]:")
    lines.append("#   Each mosaic is suffixed by a 4-letter signature indicating whether each")
    lines.append("#   respective block is symmetric under reflection ('s') or chiral/non-symmetric ('n').")
    lines.append("#")
    lines.append("# Galois Orbit Cycles:")
    lines.append("#   Monomers:  mu_1 [signature] (fixed under all mu_k)")
    lines.append("#   Dimers:    mu_1 [sig1] -> mu_3 [sig2] (interchanged by mu_3, fixed by mu_7)")
    lines.append("#   Tetramers: mu_1 [sig1] -> mu_3 [sig2] -> mu_7 [sig3] -> mu_5 [sig4] (4-cycle)")
    lines.append("#")
    lines.append("# Natural Sorting Cascade:")
    lines.append("#   Tier 1: Dihedral Orbit Size |O| (ascending: 1 -> 2 -> 4 -> 8 -> 16 -> 32)")
    lines.append("#   Tier 2: Symmetric Block Count s (descending: 4 -> 3 -> 2 -> 1 -> 0)")
    lines.append("#   Tier 3: Chord Dispersion Energy E(P) (descending: regular -> clustered)")
    lines.append("#   Tier 4: Canonical Stride Profile Multiset")
    lines.append("#   Tier 5: Canonical Lexicographic Tie-Breaker")
    lines.append("# ==============================================================================\n")

    # 1. Monomers (14)
    lines.append("# --- I. MONOMERS (1-Cycles, 14 Orbits) ---")
    fixed_orbits = find_fixed_point_orbits(16, 4, 4)
    monomers = []
    for orb in fixed_orbits:
        rep = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        sz = len(orb)
        key = get_mosaic_sort_key(rep, sz, 16)
        monomers.append((key, rep, sz))
    monomers.sort(key=lambda x: x[0])

    for idx, (key, rep, sz) in enumerate(monomers, 1):
        s_cnt = -key[1]
        energy = -key[2]
        slash_str = format_partition_slash(rep)
        sig = get_chirality_signature(rep, 16)
        lines.append(f"M{idx:02d}    Monomer   |O|={sz:<2d}  s={s_cnt}  E={energy:<4d}  {slash_str} [{sig}]")

    # 2. Dimers (295)
    lines.append("\n# --- II. DIMERS (2-Cycles, 295 Pairs / 590 Orbits) ---")
    cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "doublets.json")
    dimers = load_and_sort_dimers(cache_path)

    for idx, (key, top_p, bot_p, sz, s_cnt, e_top, e_bot) in enumerate(dimers, 1):
        slash1 = format_partition_slash(top_p)
        slash2 = format_partition_slash(bot_p)
        sig1 = get_chirality_signature(top_p, 16)
        sig2 = get_chirality_signature(bot_p, 16)
        e_str = f"{e_top}/{e_bot}"
        lines.append(f"D{idx:03d}   Dimer     |O|={sz:<2d}  s={s_cnt}  E={e_str:<7s}  {slash1} [{sig1}] -> {slash2} [{sig2}]")

    # 3. High-Symmetry Tetramers
    lines.append("\n# --- III. TETRAMERS (4-Cycles, High-Symmetry Pre-Catalogued, |O| < 32) ---")
    tetramers = extract_high_symmetry_tetramers()
    for idx, (key, cycle, sz) in enumerate(tetramers, 1):
        p1, p2, p3, p4 = cycle
        s_cnt = -key[1]
        energy = -key[2]
        s1 = format_partition_slash(p1)
        s2 = format_partition_slash(p2)
        s3 = format_partition_slash(p3)
        s4 = format_partition_slash(p4)
        sig1 = get_chirality_signature(p1, 16)
        sig2 = get_chirality_signature(p2, 16)
        sig3 = get_chirality_signature(p3, 16)
        sig4 = get_chirality_signature(p4, 16)
        cycle_str = f"{s1} [{sig1}] -> {s2} [{sig2}] -> {s3} [{sig3}] -> {s4} [{sig4}]"
        lines.append(f"T{idx:05d}  Tetramer  |O|={sz:<2d}  s={s_cnt}  E={energy:<4d}  {cycle_str}")

    content = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(content)
    print(f"✓ Generated machine-readable index at {output_file} ({len(lines)} lines)")

def main():
    parser = argparse.ArgumentParser(description="Generate canonical machine-readable cartouche index.")
    parser.add_argument("-o", "--output", default="hexdec/data/hexadecality_index.txt",
                        help="Output text file path")
    args = parser.parse_args()
    generate_index(args.output)

if __name__ == "__main__":
    main()
