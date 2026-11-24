#!/usr/bin/env python3
"""
investigate_doublet_natural_ordering.py - Explore Natural Mathematical Orderings for Doublets and Quartets

Invariants investigated:
1. Dihedral orbit size |O|.
2. Count of symmetric (achiral) vs chiral blocks (s in 0..4).
3. Stride profile multiset (the geometric shapes of the 4 inscribed quadrilaterals).
4. Compactness / Chord Energy E(P) = sum of chord lengths squared.
5. Cyclic autocorrelation / interval vector.
"""

import sys
import os
import json
import math
from collections import defaultdict, Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from hexdec.tools.generate_doublets_plates import is_block_symmetric

def get_block_strides(blk, n=16):
    sb = sorted(blk)
    strides = []
    for i in range(len(sb)):
        diff = (sb[(i + 1) % len(sb)] - sb[i]) % n
        strides.append(diff)
    # Canonical cycle representation: min under cyclic shifts and reversal
    cycles = []
    L = len(strides)
    for shift in range(L):
        c = strides[shift:] + strides[:shift]
        cycles.append(tuple(c))
        cycles.append(tuple(reversed(c)))
    return min(cycles)

def compute_mosaic_energy(blocks, n=16):
    """Sum of squared circular chord lengths within blocks."""
    total_energy = 0
    for blk in blocks:
        sb = sorted(blk)
        for i in range(len(sb)):
            for j in range(i + 1, len(sb)):
                d = min((sb[j] - sb[i]) % n, (sb[i] - sb[j]) % n)
                total_energy += d * d
    return total_energy

def analyze_doublets():
    cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "doublets.json")
    with open(cache_path) as f:
        doublets = json.load(f)
        
    print(f"=== Natural Invariant Analysis for {len(doublets)} Doublets ===")
    
    # Stratification by (orbit size, symmetric block count)
    sym_counts = defaultdict(lambda: defaultdict(int))
    energy_dist = defaultdict(list)
    profile_dist = defaultdict(int)
    
    for idx, d in enumerate(doublets):
        p1 = d["p1"]
        sz = d["sz1"]
        n_sym = sum(1 for b in p1 if is_block_symmetric(b, 16))
        sym_counts[sz][n_sym] += 1
        
        energy = compute_mosaic_energy(p1, 16)
        energy_dist[sz].append(energy)
        
        # Profile quadruple
        profiles = tuple(sorted([get_block_strides(b, 16) for b in p1]))
        profile_dist[profiles] += 1
        
    print("\n1. Stratification by Dihedral Orbit Size and Symmetric Block Count:")
    print(f"{'Orbit Size':<12} {'Sym Blocks: 4':<15} {'3 Sym':<10} {'2 Sym':<10} {'1 Sym':<10} {'0 Sym (All Chiral)':<18} {'Total Doublets'}")
    print("-" * 85)
    for sz in sorted(sym_counts.keys()):
        counts = sym_counts[sz]
        c4 = counts[4]
        c3 = counts[3]
        c2 = counts[2]
        c1 = counts[1]
        c0 = counts[0]
        tot = sum(counts.values())
        print(f"Size {sz:<7} {c4:<15} {c3:<10} {c2:<10} {c1:<10} {c0:<18} {tot}")
        
    print(f"\n2. Distinct Inscribed Shape Profile Quadruples: {len(profile_dist)}")
    print("Most frequent shape profile quadruples across doublets:")
    for prof, cnt in sorted(profile_dist.items(), key=lambda x: -x[1])[:8]:
        prof_str = " + ".join(str(p) for p in prof)
        print(f"  {cnt:3d} doublets: {prof_str}")
        
    print("\n3. Chord Energy Range per Orbit Size:")
    for sz in sorted(energy_dist.keys()):
        energies = energy_dist[sz]
        print(f"  Size {sz:2d}: Min Energy = {min(energies)}, Max Energy = {max(energies)}, Mean = {sum(energies)/len(energies):.1f}")

if __name__ == "__main__":
    analyze_doublets()
