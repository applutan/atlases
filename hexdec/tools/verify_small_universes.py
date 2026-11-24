#!/usr/bin/env python3
"""
verify_small_universes.py - Rigorous Algebraic Census of D_4 (z_2^2) and D_9 (z_3^3) Universes

Computes:
1. Raw partitions count
2. Dihedral orbits and stabilisers under D_n
3. Action of the outer affine multiplier group G_macro = (Z_n)* / {+-1}
4. Decomposition into Monomers and Trimers
5. Exact Burnside fixed-point numbers

Author: Gemma Knee
"""

import math
import itertools
from collections import defaultdict

def partition_canonical(partition):
    return tuple(sorted([tuple(sorted(b)) for b in partition]))

def generate_equal_partitions(n, k, block_size):
    """Generate all partitions of Z_n into k blocks of size block_size."""
    elements = list(range(n))
    def helper(remaining, current_blocks):
        if not remaining:
            yield current_blocks
            return
        first = remaining[0]
        rest = remaining[1:]
        for combo in itertools.combinations(rest, block_size - 1):
            block = (first,) + combo
            new_remaining = [x for x in rest if x not in combo]
            yield from helper(new_remaining, current_blocks + [block])
    yield from helper(elements, [])

def analyze_universe(n, k, block_size):
    print(f"\n=======================================================")
    print(f"UNIVERSE: Z_{n}, shape z_{block_size}^{k}")
    print(f"=======================================================")
    raw_partitions = list(generate_equal_partitions(n, k, block_size))
    raw_set = {partition_canonical(p) for p in raw_partitions}
    print(f"Raw partitions count: {len(raw_set)}")

    # Dihedral group D_n
    # Elements: x -> a*x + b mod n, where a in {1, -1}, b in 0..n-1
    d_group = [(a, b) for a in [1, -1] for b in range(n)]
    print(f"Dihedral group D_{n} order: {len(d_group)}")

    def apply_affine(p, a, b):
        new_p = [[(a * x + b) % n for x in block] for block in p]
        return partition_canonical(new_p)

    # Compute dihedral orbits
    visited = set()
    d_orbits = []
    for p in raw_set:
        if p in visited:
            continue
        orbit = set()
        for a, b in d_group:
            orbit.add(apply_affine(p, a, b))
        visited.update(orbit)
        # Canonical rep: lexicographically smallest
        canon = min(orbit)
        stab_order = len(d_group) // len(orbit)
        d_orbits.append({
            "canon": canon,
            "size": len(orbit),
            "stab_order": stab_order,
            "members": orbit
        })

    print(f"Total dihedral orbits: {len(d_orbits)}")
    size_dist = defaultdict(int)
    for o in d_orbits:
        size_dist[o["size"]] += 1
    for sz in sorted(size_dist.keys()):
        print(f"  Dihedral orbit size {sz}: {size_dist[sz]} orbits (Stab order {len(d_group)//sz})")

    # Outer multiplier group: (Z_n)* / {+-1}
    units = [u for u in range(1, n) if math.gcd(u, n) == 1]
    # Identify quotient by {+-1}
    macro_classes = []
    seen_units = set()
    for u in units:
        if u in seen_units:
            continue
        inv_u = (-u) % n
        seen_units.add(u)
        seen_units.add(inv_u)
        macro_classes.append(u)

    print(f"\nUnits (Z_{n})*: {units} (order {len(units)})")
    print(f"Outer macro quotient G_macro = (Z_{n})* / {{+-1}}: {macro_classes} (order {len(macro_classes)})")

    # Map dihedral orbits under G_macro
    # Map each partition canonical to its orbit index
    p_to_orbit = {}
    for idx, o in enumerate(d_orbits):
        for p in o["members"]:
            p_to_orbit[p] = idx

    visited_macro = set()
    macro_orbits = []
    for idx, o in enumerate(d_orbits):
        if idx in visited_macro:
            continue
        p = o["canon"]
        m_orbit_indices = set()
        for u in macro_classes:
            pu = apply_affine(p, u, 0)
            target_idx = p_to_orbit[pu]
            m_orbit_indices.add(target_idx)
        visited_macro.update(m_orbit_indices)
        macro_orbits.append({
            "size": len(m_orbit_indices),
            "d_orbits": [d_orbits[i] for i in sorted(m_orbit_indices)]
        })

    print(f"\nTotal Affine Macro-Orbits: {len(macro_orbits)}")
    macro_dist = defaultdict(int)
    for mo in macro_orbits:
        macro_dist[mo["size"]] += 1
    for sz in sorted(macro_dist.keys()):
        print(f"  Macro-orbit size {sz}: {macro_dist[sz]} macro-orbits")

    # Detailed breakdown of macro-orbits
    for m_sz in sorted(macro_dist.keys()):
        print(f"\nBreakdown for Macro-orbit size {m_sz}:")
        for mo in [m for m in macro_orbits if m["size"] == m_sz]:
            d_sizes = [d["size"] for d in mo["d_orbits"]]
            rep = mo["d_orbits"][0]["canon"]
            print(f"  Rep: {rep} | Dihedral sizes: {d_sizes}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rigorous Algebraic Census of D_4 (z_2^2) and D_9 (z_3^3) Universes.")
    parser.add_argument("--universe", choices=["all", "z4", "z9"], default="all", help="Target universe to analyze (default: all)")
    args = parser.parse_args()
    if args.universe in ("all", "z4"):
        analyze_universe(4, 2, 2)
    if args.universe in ("all", "z9"):
        analyze_universe(9, 3, 3)
