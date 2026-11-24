#!/usr/bin/env python3
"""
compute_all_d16_orbit_sizes.py - Exact Dihedral Orbit Size Breakdown of all 83,488 Mosaics
"""

import sys
import os
import math
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import count_fixed_partitions

def compute_all_d16_orbit_distribution(n=16, k=4, s=4):
    # D_16 has elements (a, b) with a in {1, 15}, b in 0..15.
    # Group elements into conjugacy classes:
    # 1. Identity: (1, 0) - order 1
    # 2. Central half-turn: (1, 8) - order 2
    # 3. Rotations of order 4: (1, 4), (1, 12) - 2 elements
    # 4. Rotations of order 8: (1, 2), (1, 6), (1, 10), (1, 14) - 4 elements
    # 5. Rotations of order 16: (1, 1), (1, 3), (1, 5), (1, 7), (1, 9), (1, 11), (1, 13), (1, 15) - 8 elements
    # 6. Reflections class 1 (even shifts): (15, 0), (15, 2), ..., (15, 14) - 8 elements
    # 7. Reflections class 2 (odd shifts): (15, 1), (15, 3), ..., (15, 15) - 8 elements
    
    classes = [
        ("Identity (1,0)", [(1, 0)], 1),
        ("Half-turn (1,8)", [(1, 8)], 1),
        ("Rotations order 4", [(1, 4), (1, 12)], 2),
        ("Rotations order 8", [(1, 2), (1, 6), (1, 10), (1, 14)], 4),
        ("Rotations order 16", [(1, 1), (1, 3), (1, 5), (1, 7), (1, 9), (1, 11), (1, 13), (1, 15)], 8),
        ("Reflections even", [(15, 2 * i) for i in range(8)], 8),
        ("Reflections odd", [(15, 2 * i + 1) for i in range(8)], 8),
    ]
    
    fix_counts = {}
    for name, elems, size in classes:
        # Pick representative
        a, b = elems[0]
        perm = [(a * x + b) % n for x in range(n)]
        fix_c = count_fixed_partitions(perm, k, s)
        fix_counts[name] = fix_c
        print(f"Class '{name}' ({size} elements): Fix(g) = {fix_c}")
        
    # Total fixed sum over D_16 = 32 * 83488 = 2,671,616
    total_fix = sum(len(elems) * fix_counts[name] for name, elems, size in classes)
    total_orbits = total_fix // 32
    print(f"\nTotal D_16 Orbits: {total_orbits} (expected 83,488)")
    
    # We can also compute for C_16:
    c16_classes = classes[:5]
    total_fix_c16 = sum(len(elems) * fix_counts[name] for name, elems, size in c16_classes)
    total_c16_orbits = total_fix_c16 // 16
    print(f"Total C_16 Orbits: {total_c16_orbits} (expected 164,491)")

if __name__ == "__main__":
    compute_all_d16_orbit_distribution()
