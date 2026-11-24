#!/usr/bin/env python3
"""
lookup_mosaic.py - Canonical Dihedral Reduction & Affine Macro-Orbit Cartouche Lookup

Given any composition mosaic partition on Z_16 (e.g. /017A/289F/36CD/45BE/):
1. Determines its canonical dihedral orbit representative under D_16.
2. Computes its dihedral orbit size |O|, symmetric block count s, chord energy E, and chirality signature.
3. Identifies its parent Affine Macro-Orbit Cartouche ID (Monomer M_k, Dimer D_k, or Tetramer T_k)
   and its exact phase (mu_1, mu_3, mu_7, or mu_5).
4. Emits its orbital comosaics in both dilated and canonical forms.

Author: Gemma Knee
"""

import sys
import os
import argparse
from typing import List, Tuple, Set

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import find_fixed_point_orbits
from hexdec.tools.generate_dimers_plates import load_and_sort_dimers
from hexdec.tools.mosaic_sorting import (
    get_mosaic_sort_key,
    is_block_symmetric,
    compute_mosaic_chord_energy,
    get_chirality_signature,
    get_block_canonical_stride,
    format_partition_slash,
)

n = 16
d_n_elements = [(a, b) for a in [1, 15] for b in range(16)]

def parse_partition_slash(slash_str: str) -> List[List[int]]:
    """Parse string like /017A/289F/36CD/45BE/ into list of blocks."""
    cleaned = slash_str.strip().strip("/")
    parts = cleaned.split("/")
    hex_map = {c: int(c, 16) for c in "0123456789ABCDEFabcdef"}
    blocks = []
    for p in parts:
        blk = sorted([hex_map[c] for c in p])
        blocks.append(blk)
    blocks.sort(key=lambda b: (min(b), b))
    return blocks

def get_dihedral_orbit(part: List[List[int]]) -> Set[Tuple[Tuple[int, ...], ...]]:
    """Return all partition configurations in the D_16 orbit."""
    orb = set()
    for a, b in d_n_elements:
        p = tuple(sorted(tuple(sorted((a * x + b) % n for x in blk)) for blk in part))
        orb.add(p)
    return orb

def get_canonical_rep(part: List[List[int]]) -> List[List[int]]:
    """Return the lexicographically smallest partition in the D_16 orbit."""
    orb = get_dihedral_orbit(part)
    min_p = min(orb)
    return [list(b) for b in min_p]

def apply_multiplier(part: List[List[int]], mult: int) -> List[List[int]]:
    """Apply modular multiplier x -> (mult * x) % 16."""
    p = [sorted((mult * x) % n for x in blk) for blk in part]
    p.sort(key=lambda b: (min(b), b))
    return p

def main():
    parser = argparse.ArgumentParser(description="Lookup any Z_16 composition mosaic in the Affine Cartouche Catalogues.")
    parser.add_argument("partition", nargs="?", default=None,
                        help="Partition in slash notation (e.g. /056B/127C/38DE/49AF/)")
    parser.add_argument("-p", "--partition", dest="opt_partition", metavar="PARTITION", default=None,
                        help="Partition in slash notation (optional flag equivalent to positional argument)")
    args = parser.parse_args()

    partition_str = args.opt_partition or args.partition or "/056B/127C/38DE/49AF/"
    input_part = parse_partition_slash(partition_str)
    canon_part = get_canonical_rep(input_part)
    orb = get_dihedral_orbit(input_part)
    orb_sz = len(orb)

    s_count = sum(1 for b in canon_part if is_block_symmetric(b, n))
    energy = compute_mosaic_chord_energy(canon_part, n)
    sig_input = get_chirality_signature(input_part, n)
    sig_canon = get_chirality_signature(canon_part, n)

    print("=" * 80)
    print("HEXADECALITY: COMPOSITION MOSAIC ORBIT & CARTOUCHE RESOLVER")
    print("=" * 80)
    print(f"Input Partition:       {format_partition_slash(input_part)}  [{sig_input}]")
    print(f"Canonical Dihedral D16:{format_partition_slash(canon_part)}  [{sig_canon}]")
    print(f"Dihedral Orbit Size:   |O| = {orb_sz} (Stabiliser order: {32 // orb_sz})")
    print(f"Symmetric Blocks:      s = {s_count} of 4 (Achiral)")
    print(f"Chord Energy:          E = {energy}")
    print("-" * 80)

    # Compute orbital comosaics under mu_3
    # Check if Monomer, Dimer, or Tetramer
    p_mu1 = input_part
    p_mu3 = apply_multiplier(input_part, 3)
    p_mu7 = apply_multiplier(input_part, 7)
    p_mu5 = apply_multiplier(input_part, 5)

    c_mu1 = get_canonical_rep(p_mu1)
    c_mu3 = get_canonical_rep(p_mu3)
    c_mu7 = get_canonical_rep(p_mu7)
    c_mu5 = get_canonical_rep(p_mu5)

    # Determine type
    if c_mu1 == c_mu3:
        macro_type = "Monomer (1-Cycle)"
    elif c_mu1 == c_mu7:
        macro_type = "Dimer (2-Cycle)"
    else:
        macro_type = "Tetramer (4-Cycle)"

    print(f"Affine Macro-Orbit Type: {macro_type}")
    print("\nOrbital Comosaics Cycle (Physical Dilation vs Canonical Rep):")
    phases = [
        ("Phase 1 (mu_1 = id)", p_mu1, c_mu1),
        ("Phase 2 (mu_3 = x3)", p_mu3, c_mu3),
        ("Phase 3 (mu_7 = x7)", p_mu7, c_mu7),
        ("Phase 4 (mu_5 = x5)", p_mu5, c_mu5),
    ]

    for label, dilated, canon in phases:
        d_slash = format_partition_slash(dilated)
        d_sig = get_chirality_signature(dilated, n)
        c_slash = format_partition_slash(canon)
        c_sig = get_chirality_signature(canon, n)
        is_same = (d_slash == c_slash)
        status = "(Identical to canonical)" if is_same else f"(Canonical is rotated/reflected: {c_slash})"
        print(f"  {label:<21s}: {d_slash} [{d_sig}] {status}")

    print("=" * 80)

if __name__ == "__main__":
    main()
