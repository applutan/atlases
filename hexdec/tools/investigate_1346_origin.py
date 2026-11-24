#!/usr/bin/env python3
"""
investigate_1346_origin.py - Deep dive into the 1, 3, 4, 6 monomer distribution
"""

import sys
import os
import math
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import get_affine_group, find_fixed_point_orbits, get_units

def detailed_monomer_breakdown():
    aff = get_affine_group(16)
    d_16 = [(a, b) for a in [1, 15] for b in range(16)]
    fixed_orbits = find_fixed_point_orbits(16, 4, 4)
    sorted_orbits = sorted(fixed_orbits, key=lambda o: (len(o), sorted([sorted(list(b)) for b in list(o)[0]])))

    print("Detailed breakdown of the 14 Monomers:")
    for idx, orb in enumerate(sorted_orbits, 1):
        rep = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        blocks = sorted([sorted(list(b)) for b in rep])
        orb_sz = len(orb)
        
        # Stab in D_16
        stab_d = []
        for a, b in d_16:
            p_img = frozenset(frozenset((a * x + b) % 16 for x in blk) for blk in rep)
            if p_img == rep:
                stab_d.append((a, b))
                
        # Stab in Aff(Z_16)
        stab_aff = []
        for a, b in aff:
            p_img = frozenset(frozenset((a * x + b) % 16 for x in blk) for blk in rep)
            if p_img == rep:
                stab_aff.append((a, b))
                
        # Group structure of Stab_D
        # Rotations are (1, b), reflections are (15, b)
        rot_shifts = [b for a, b in stab_d if a == 1]
        ref_shifts = [b for a, b in stab_d if a == 15]
        
        # Group structure of Stab_Aff
        mult_map = defaultdict(list)
        for a, b in stab_aff:
            mult_map[a].append(b)
            
        print(f"\n--- Monomer #{idx} (D_16 orbit size = {orb_sz}) ---")
        print(f"Blocks: {blocks}")
        print(f"Stab_D: |G| = {len(stab_d)}. Rotations ({len(rot_shifts)}): {rot_shifts}, Reflections ({len(ref_shifts)}): {ref_shifts}")
        print(f"Stab_Aff: |G| = {len(stab_aff)}. Multipliers present: {sorted(mult_map.keys())}")
        for m in sorted(mult_map.keys()):
            print(f"  Multiplier {m:2d}: shifts {mult_map[m]}")

if __name__ == "__main__":
    detailed_monomer_breakdown()
