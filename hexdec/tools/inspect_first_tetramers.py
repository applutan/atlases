#!/usr/bin/env python3
"""
inspect_first_tetramers.py - Extract and sort the first high-symmetry Tetramers under the natural cascade.
"""

import sys
import os
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import get_fixed_partitions
from hexdec.tools.mosaic_sorting import (
    get_mosaic_sort_key,
    is_block_symmetric,
    compute_mosaic_chord_energy,
    get_block_canonical_stride,
)

def extract_high_symmetry_tetramers(n=16, k=4, s=4):
    d_n_elements = [(a, b) for a in [1, 15] for b in range(16)]

    def apply_d(part, a, b):
        return frozenset(frozenset((a * x + b) % n for x in blk) for blk in part)

    def apply_mu(part, mult):
        return frozenset(frozenset((mult * x) % n for x in blk) for blk in part)

    order2_elements = [(1, 8)] + [(15, b) for b in range(16)]
    all_fixed = set()
    for a, b in order2_elements:
        perm = [(a * x + b) % n for x in range(n)]
        pts = get_fixed_partitions(perm, 4, 4)
        all_fixed.update(pts)

    orbits = {}
    visited = set()
    for p in all_fixed:
        if p in visited:
            continue
        orb = frozenset(apply_d(p, a, b) for a, b in d_n_elements)
        visited.update(orb)
        orbits[orb] = len(orb)

    visited_orbs = set()
    tetramers = []

    for o, sz in orbits.items():
        if o in visited_orbs:
            continue
        rep = sorted(list(o), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        rep_mu3 = apply_mu(rep, 3)
        o2 = frozenset(apply_d(rep_mu3, a, b) for a, b in d_n_elements)
        if o2 == o:
            continue
        rep_mu9 = apply_mu(rep_mu3, 3)
        o3 = frozenset(apply_d(rep_mu9, a, b) for a, b in d_n_elements)
        if o3 == o:
            continue
        rep_mu27 = apply_mu(rep_mu9, 3)
        o4 = frozenset(apply_d(rep_mu27, a, b) for a, b in d_n_elements)

        visited_orbs.add(o)
        visited_orbs.add(o2)
        visited_orbs.add(o3)
        visited_orbs.add(o4)

        # For each of the 4 orbits, find canonical cycle where p1 has highest symmetry/energy
        candidate_cycles = []
        for cand_o in [o, o2, o3, o4]:
            c_rep = sorted(list(cand_o), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
            cp1 = [sorted(list(b)) for b in c_rep]
            cp2 = sorted([sorted([(3 * x) % 16 for x in b]) for b in cp1])
            cp3 = sorted([sorted([(7 * x) % 16 for x in b]) for b in cp1])
            cp4 = sorted([sorted([(5 * x) % 16 for x in b]) for b in cp1])

            s_count = sum(1 for b in cp1 if is_block_symmetric(b, 16))
            e = compute_mosaic_chord_energy(cp1, 16)
            strides = tuple(sorted(get_block_canonical_stride(b, 16) for b in cp1))
            key = (sz, -s_count, -e, strides, tuple(tuple(b) for b in cp1))
            candidate_cycles.append((key, (cp1, cp2, cp3, cp4)))

        candidate_cycles.sort(key=lambda x: x[0])
        best_key, best_cycle = candidate_cycles[0]
        tetramers.append((best_key, best_cycle, sz))

    tetramers.sort(key=lambda x: x[0])
    return tetramers

def format_partition_slash(p):
    """Format partition as /0149/26AE/37BF/58CD/ using single hexadecimal characters."""
    blocks = sorted([sorted(list(b)) for b in p])
    hex_chars = "0123456789ABCDEF"
    parts = []
    for blk in blocks:
        parts.append("".join(hex_chars[x] for x in blk))
    return "/" + "/".join(parts) + "/"

def main():
    tetramers = extract_high_symmetry_tetramers()
    print(f"Total Tetramers extracted with size < 32: {len(tetramers)}")
    print(f"{'Idx':<4} {'Size':<6} {'Sym':<5} {'Energy':<8} {'Canonical Strides':<45} {'Partition-Slash'}")
    print("-" * 115)
    for idx, (key, cycle, sz) in enumerate(tetramers[:20], 1):
        p1 = cycle[0]
        s_count = sum(1 for b in p1 if is_block_symmetric(b, 16))
        e = compute_mosaic_chord_energy(p1, 16)
        strides = " + ".join(str(st) for st in key[3])
        slash_rep = format_partition_slash(p1)
        print(f"{idx:<4} {sz:<6} {s_count:<5} {e:<8} {strides:<45} {slash_rep}")

if __name__ == "__main__":
    main()
