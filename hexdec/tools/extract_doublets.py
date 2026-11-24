#!/usr/bin/env python3
"""
extract_doublets.py - Extract and Catalog all 295 Doublets of z_4^4 on Z_16

A doublet is an affine macro-orbit consisting of a 2-cycle {O_a, O_b} under mu_3:
  mu_3(O_a) = O_b,  mu_3(O_b) = O_a
  mu_7(O_a) = O_a,  mu_7(O_b) = O_b

Algorithm:
1. Find all partitions fixed by affine elements with multiplier in {7, 9}.
2. Group into D_16 orbits.
3. Remove the 14 monomers (which are fixed by mu_3).
4. Pair up the remaining orbits under mu_3 into 295 doublets.
5. Sort each doublet canonically and rank them.
"""

import sys
import os
import time
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import get_fixed_partitions, find_fixed_point_orbits

def get_canonical_partition_rep(orb, n=16):
    """Return the lexicographically smallest partition representation for a D_n orbit."""
    sorted_p = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))
    return sorted_p[0]

def extract_all_doublets(n=16, k=4, s=4):
    t0 = time.time()
    d_n_elements = [(a, b) for a in [1, n - 1] for b in range(n)]
    
    def apply_d(part, a, b):
        return frozenset(frozenset((a * x + b) % n for x in blk) for blk in part)
        
    def apply_mu(part, mult):
        return frozenset(frozenset((mult * x) % n for x in blk) for blk in part)

    print(f"Finding fixed partitions for multipliers in {{7, 9}}...")
    mu7_units = [7, (n - 7) % n]  # 7 and 9 for n=16
    candidate_partitions = set()
    for a in mu7_units:
        for b in range(n):
            perm = [(a * x + b) % n for x in range(n)]
            parts = get_fixed_partitions(perm, k, s)
            candidate_partitions.update(parts)
            
    print(f"Total partitions fixed by some element in D_16 * mu_7: {len(candidate_partitions)}")
    
    # Group into D_16 orbits
    visited = set()
    mu7_fixed_orbits = []
    
    for p in candidate_partitions:
        if p in visited:
            continue
        orb = set()
        for a, b in d_n_elements:
            orb.add(apply_d(p, a, b))
        visited.update(orb)
        
        # Verify orbit is preserved by mu_7
        p_mu7 = apply_mu(p, 7)
        if p_mu7 in orb:
            mu7_fixed_orbits.append(frozenset(orb))
            
    print(f"Total D_16 orbits fixed by mu_7: {len(mu7_fixed_orbits)}")
    
    # Get the 14 monomers to exclude them
    monomer_orbits = [frozenset(o) for o in find_fixed_point_orbits(n, k, s)]
    monomer_set = set(monomer_orbits)
    print(f"Confirmed monomers to exclude: {len(monomer_set)}")
    
    # Filter out monomers
    doublet_candidate_orbits = [o for o in mu7_fixed_orbits if o not in monomer_set]
    print(f"Remaining D_16 orbits (should be 590): {len(doublet_candidate_orbits)}")
    
    # Pair up orbits under mu_3
    paired = set()
    doublets = []
    
    # Map each orbit to its canonical representative
    orbit_reps = {o: get_canonical_partition_rep(o, n) for o in doublet_candidate_orbits}
    
    # Helper to find orbit of a partition
    def find_orbit_of_partition(part):
        for o in doublet_candidate_orbits:
            if part in o:
                return o
        return None

    for o1 in doublet_candidate_orbits:
        if o1 in paired:
            continue
        p1 = orbit_reps[o1]
        p1_mu3 = apply_mu(p1, 3)
        o2 = find_orbit_of_partition(p1_mu3)
        if o2 is None or o2 == o1:
            print(f"Warning: unexpected orbit pairing for {p1}")
            continue
        paired.add(o1)
        paired.add(o2)
        
        # Canonical order of pair (O_a, O_b)
        rep1 = orbit_reps[o1]
        rep2 = orbit_reps[o2]
        sort_key1 = sorted([sorted(list(b)) for b in rep1])
        sort_key2 = sorted([sorted(list(b)) for b in rep2])
        if sort_key1 <= sort_key2:
            top_p = [sorted(list(b)) for b in rep1]
            bot_p = sorted([sorted([(3 * x) % n for x in b]) for b in top_p])
            doublets.append((top_p, bot_p, len(o1), len(o2)))
        else:
            top_p = [sorted(list(b)) for b in rep2]
            bot_p = sorted([sorted([(3 * x) % n for x in b]) for b in top_p])
            doublets.append((top_p, bot_p, len(o2), len(o1)))
            
    # Sort doublets canonically by orbit size, then canonical top rep
    doublets.sort(key=lambda d: (
        d[2], # Orbit size of O_a
        d[3], # Orbit size of O_b
        sorted([sorted(list(b)) for b in d[0]]),
        sorted([sorted(list(b)) for b in d[1]])
    ))
    
    t1 = time.time()
    print(f"Successfully extracted {len(doublets)} doublets in {t1 - t0:.2f}s!")
    
    # Orbit size distribution of doublets
    size_pairs = defaultdict(int)
    for rep1, rep2, sz1, sz2 in doublets:
        size_pairs[(sz1, sz2)] += 1
        
    print("\nDoublet orbit size distribution:")
    for pair, cnt in sorted(size_pairs.items()):
        print(f"  Orbit sizes {pair}: {cnt} doublets ({cnt * 2} D_16 orbits)")
        
    return doublets

if __name__ == "__main__":
    doublets = extract_all_doublets(16, 4, 4)
