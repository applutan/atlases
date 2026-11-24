#!/usr/bin/env python3
"""
monomer_symmetry_analysis.py - Detailed Algebraic & Stabilizer Analysis of Monomers

Investigates:
1. Stabilizers in D_16 and Aff(Z_16) for each of the 14 monomers of z_4^4.
2. Why orbit sizes are strictly {1, 4, 16, 32} and counts are (1, 3, 4, 6).
3. Why orbit sizes 2 and 8 do not appear.
4. Testing whether the total count 14 being the Catalan number C_4 = 14 is a
   combinatorial isomorphism (e.g. via NC(4)) or an accidental numerical coincidence.
5. Macro-orbit fixed points across other equal-block shapes z_s^k.
"""

import sys
import os
import math
import argparse
from collections import defaultdict

# Add parent directory for tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import get_affine_group, find_fixed_point_orbits, get_units

def analyze_monomer_stabilizers(n=16, k=4, s=4):
    aff = get_affine_group(n)
    d_n = [(a, b) for a in [1, n - 1] for b in range(n)]
    
    fixed_orbits = find_fixed_point_orbits(n, k, s)
    sorted_orbits = sorted(fixed_orbits, key=lambda o: (len(o), sorted([sorted(list(b)) for b in list(o)[0]])))
    
    print(f"=== Analysis of {len(sorted_orbits)} Monomers for z_{s}^{k} on Z_{n} ===")
    
    orbit_size_counts = defaultdict(int)
    
    for idx, orb in enumerate(sorted_orbits, 1):
        # Choose canonical representative
        rep = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        orb_sz = len(orb)
        orbit_size_counts[orb_sz] += 1
        
        # Calculate Stabilizer in D_n
        stab_d = []
        for a, b in d_n:
            p_img = frozenset(frozenset((a * x + b) % n for x in blk) for blk in rep)
            if p_img == rep:
                stab_d.append((a, b))
                
        # Calculate Stabilizer in Aff(Z_n)
        stab_aff = []
        for a, b in aff:
            p_img = frozenset(frozenset((a * x + b) % n for x in blk) for blk in rep)
            if p_img == rep:
                stab_aff.append((a, b))
                
        # Multipliers present in Stab_Aff
        mults_aff = sorted(list(set(a for a, b in stab_aff)))
        
        # Rotations and reflections in Stab_D
        rot_d = [b for a, b in stab_d if a == 1]
        ref_d = [b for a, b in stab_d if a == n - 1]
        
        print(f"Monomer #{idx:2d}: |O_D| = {orb_sz:2d} | |Stab_D| = {len(stab_d):2d} (rot: {len(rot_d)}, ref: {len(ref_d)}) | |Stab_Aff| = {len(stab_aff):2d} | Mults in Stab: {mults_aff}")
        
    print("\nOrbit size distribution:")
    for sz in sorted(orbit_size_counts.keys()):
        print(f"  Size {sz:2d}: {orbit_size_counts[sz]} monomer(s)")
    print(f"Total monomers: {sum(orbit_size_counts.values())}")

def compare_catalan_and_other_shapes():
    """Check fixed point monomers for various z_s^k to see if Catalan numbers generalise."""
    print("\n=== Survey of Monomer Counts for Various z_s^k ===")
    cases = [
        (8, 2, 4),   # z_4^2 on Z_8 (k=2 blocks, C_2 = 2)
        (8, 4, 2),   # z_2^4 on Z_8 (k=4 blocks, C_4 = 14)
        (9, 3, 3),   # z_3^3 on Z_9 (k=3 blocks, C_3 = 5)
        (12, 2, 6),  # z_6^2 on Z_12
        (12, 3, 4),  # z_4^3 on Z_12 (C_3 = 5)
        (12, 4, 3),  # z_3^4 on Z_12 (C_4 = 14)
        (12, 6, 2),  # z_2^6 on Z_12
        (16, 2, 8),  # z_8^2 on Z_16 (k=2 blocks, C_2 = 2)
        (16, 4, 4),  # z_4^4 on Z_16 (k=4 blocks, C_4 = 14)
        (16, 8, 2),  # z_2^8 on Z_16 (k=8 blocks)
    ]
    
    for n, k, s in cases:
        fps = find_fixed_point_orbits(n, k, s)
        counts = defaultdict(int)
        for o in fps:
            counts[len(o)] += 1
        dist_str = ", ".join(f"{cnt}*[sz {sz}]" for sz, cnt in sorted(counts.items()))
        print(f"Z_{n:2d}, z_{s}^{k} (k={k}, s={s}): {len(fps):3d} monomers | Distribution: {dist_str}")

def main():
    parser = argparse.ArgumentParser(description="Analyze symmetries and stabilizer subgroups of monomers.")
    parser.add_argument("--survey", action="store_true", help="Survey other shapes to test Catalan coincidence")
    args = parser.parse_args()
    
    analyze_monomer_stabilizers(16, 4, 4)
    if args.survey:
        compare_catalan_and_other_shapes()

if __name__ == "__main__":
    main()
