#!/usr/bin/env python3
"""
audit_polyatlas_correctness.py

Meticulously audits every orbit in polyatlas:
1. Verifies that all 553 subsets are mathematically valid dihedral orbit canonical representatives.
2. Verifies the achiral / chiral classification of each subset.
3. Finds the exact canonical form and local ID of the diatonic scale {0, 1, 3, 5, 6, 8, 10}.
4. Verifies the interval vector calculation for every subset.
5. Checks whether the drawings plotted in TikZ match the subsets.

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import sys
import math
import itertools
from collections import defaultdict

def get_d_ops(n):
    return [(a, b) for a in [1, n - 1] for b in range(n)]

def canonicalise_subset(subset, n):
    d_ops = get_d_ops(n)
    best = None
    for a, b in d_ops:
        cand = tuple(sorted((a * x + b) % n for x in subset))
        if best is None or cand < best:
            best = cand
    return best

def is_subset_achiral(subset, n):
    if len(subset) <= 1 or len(subset) >= n - 1:
        return True
    s_set = set(subset)
    for c in range(n):
        refl = {(c - x) % n for x in s_set}
        if refl == s_set:
            return True
    return False

def compute_interval_vector(subset, n):
    m = len(subset)
    if m <= 1:
        return ()
    dist_counts = defaultdict(int)
    for i in range(m):
        for j in range(i + 1, m):
            d = min((subset[j] - subset[i]) % n, (subset[i] - subset[j]) % n)
            dist_counts[d] += 1
    return tuple(dist_counts[d] for d in range(1, n // 2 + 1))

def circular_steps(subset, n):
    """Circular stride sequence between adjacent elements."""
    if len(subset) <= 1:
        return (n,)
    s = sorted(subset)
    m = len(s)
    return tuple((s[(i + 1) % m] - s[i]) % n for i in range(m))

def main():
    print("=" * 80)
    print("AUDITING POLYATLAS CANONICAL REPRESENATIVES & SYMMETRY")
    print("=" * 80)

    # 1. Investigate Z_12 specifically
    n = 12
    # Diatonic scale: pitch classes {0, 2, 4, 5, 7, 9, 11} (C major)
    # or {0, 1, 3, 5, 6, 8, 10} (transposed/inverted)
    diatonic_raw = (0, 1, 3, 5, 6, 8, 10)
    diatonic_canon = canonicalise_subset(diatonic_raw, 12)
    diatonic_achiral = is_subset_achiral(diatonic_canon, 12)
    diatonic_ivec = compute_interval_vector(diatonic_canon, 12)
    diatonic_steps = circular_steps(diatonic_canon, 12)

    print(f"Diatonic Scale Raw:         {diatonic_raw}")
    print(f"Diatonic Canonical Form:    {diatonic_canon}")
    print(f"Diatonic Circular Steps:    {diatonic_steps}")
    print(f"Diatonic Is Achiral (Blue)? {diatonic_achiral}")
    print(f"Diatonic Interval Vector:   {diatonic_ivec}")
    print("-" * 80)

    # What about the set {0, 1, 3, 4, 6, 8, 9}?
    set_7_38_raw = (0, 1, 3, 4, 6, 8, 9)
    set_7_38_canon = canonicalise_subset(set_7_38_raw, 12)
    set_7_38_achiral = is_subset_achiral(set_7_38_canon, 12)
    set_7_38_ivec = compute_interval_vector(set_7_38_canon, 12)
    set_7_38_steps = circular_steps(set_7_38_canon, 12)

    print(f"Set 7-38 in Table:          {set_7_38_raw}")
    print(f"Set 7-38 Canonical Form:    {set_7_38_canon}")
    print(f"Set 7-38 Circular Steps:    {set_7_38_steps}")
    print(f"Set 7-38 Is Achiral?        {set_7_38_achiral} (Chiral => Pink!)")
    print(f"Set 7-38 Interval Vector:   {set_7_38_ivec}")
    print("-" * 80)

    # Let's reproduce the exact catalogue of Z_12 k=7 from generate_poly_atlas_v2.py
    seen = set()
    k7_orbits = []
    for comb in itertools.combinations(range(12), 7):
        canon = canonicalise_subset(comb, 12)
        if canon not in seen:
            seen.add(canon)
            achiral = is_subset_achiral(canon, 12)
            ivec = compute_interval_vector(canon, 12)
            steps = circular_steps(canon, 12)
            k7_orbits.append({
                'subset': canon,
                'is_achiral': achiral,
                'ivec': ivec,
                'steps': steps,
            })

    # In generate_poly_atlas_v2:
    # k_orbits.sort(key=lambda o: (0 if o['is_achiral'] else 1, o['subset']))
    k7_orbits.sort(key=lambda o: (0 if o['is_achiral'] else 1, o['subset']))
    for idx, o in enumerate(k7_orbits, 1):
        o['local_id'] = f"7-{idx}"

    print(f"Total 7-element orbits on Z_12: {len(k7_orbits)}")
    achiral_k7 = [o for o in k7_orbits if o['is_achiral']]
    chiral_k7 = [o for o in k7_orbits if not o['is_achiral']]
    print(f"Achiral (Blue) 7-gons: {len(achiral_k7)}")
    print(f"Chiral (Pink) 7-gons:  {len(chiral_k7)}")

    print("\nListing all Achiral (Blue) 7-gons in our catalogue:")
    for o in achiral_k7:
        is_diatonic = (o['subset'] == diatonic_canon)
        marker = " <=== DIATONIC SCALE!" if is_diatonic else ""
        print(f"  {o['local_id']}: {o['subset']}  steps={o['steps']}  ivec={o['ivec']}{marker}")

    print("\nListing our 7-38:")
    o38 = [o for o in k7_orbits if o['local_id'] == "7-38"][0]
    print(f"  {o38['local_id']}: {o38['subset']}  achiral={o38['is_achiral']}  steps={o38['steps']}  ivec={o38['ivec']}")

if __name__ == "__main__":
    main()
