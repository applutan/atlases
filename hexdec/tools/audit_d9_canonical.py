#!/usr/bin/env python3
"""
audit_d9_canonical.py - Deep audit of D_9 Trimers:
Check whether:
1. Macro-orbits (Trimers T1..T8) are sorted by the 5-tier cascade (|O| asc, s desc, E desc, strides, lex).
2. For each Trimer, which of the 3 member dihedral orbits is chosen as the canonical representative (head of the 3-strip).

Author: Gemma Knee
"""

import math
import itertools

def partition_canonical(p, n=9):
    """Return lexicographical minimum over all 18 dihedral symmetries."""
    d_group = [(a, b) for a in [1, -1] for b in range(n)]
    candidates = []
    for a, b in d_group:
        cand = tuple(sorted([tuple(sorted([(a * x + b) % n for x in blk])) for blk in p]))
        candidates.append(cand)
    return min(candidates)

def get_cyclic_strides(block, n=9):
    sb = sorted(list(block))
    L = len(sb)
    strides = [(sb[(i + 1) % L] - sb[i]) % n for i in range(L)]
    candidates = []
    for i in range(L):
        shift = strides[i:] + strides[:i]
        candidates.append(tuple(shift))
        rev = list(reversed(shift))
        rev = rev[-1:] + rev[:-1]
        candidates.append(tuple(rev))
    return min(candidates)

def is_block_symmetric(block, n=9):
    sb = sorted(list(block))
    for c in range(n):
        ref_b = sorted([(-x + c) % n for x in sb])
        if ref_b == sb:
            return True
    return False

def compute_chord_energy(blocks, n=9):
    total = 0
    for blk in blocks:
        sb = sorted(list(blk))
        L = len(sb)
        for i in range(L):
            for j in range(i + 1, L):
                d = min((sb[j] - sb[i]) % n, (sb[i] - sb[j]) % n)
                total += d * d
    return total

def p_to_str(p):
    return "/" + "/".join("".join(str(x) for x in b) for b in p) + "/"

def full_d9_census():
    # Generate all 280 partitions
    elements = list(range(9))
    def helper(remaining, current_blocks):
        if not remaining:
            yield current_blocks
            return
        first = remaining[0]
        rest = remaining[1:]
        for combo in itertools.combinations(rest, 2):
            block = (first,) + combo
            new_remaining = [x for x in rest if x not in combo]
            yield from helper(new_remaining, current_blocks + [block])

    raw_set = {tuple(sorted([tuple(sorted(b)) for b in p])) for p in helper(elements, [])}

    # Group into dihedral orbits
    d_group = [(a, b) for a in [1, -1] for b in range(9)]
    visited = set()
    d_orbits = []
    for p in raw_set:
        if p in visited:
            continue
        orbit = set()
        for a, b in d_group:
            p_img = tuple(sorted([tuple(sorted([(a * x + b) % 9 for x in blk])) for blk in p]))
            orbit.add(p_img)
        visited.update(orbit)
        canon = min(orbit)
        d_orbits.append({
            "canon": canon,
            "size": len(orbit),
            "members": orbit,
            "s": sum(1 for b in canon if is_block_symmetric(b, 9)),
            "E": compute_chord_energy(canon, 9),
            "strides": sorted([get_cyclic_strides(b, 9) for b in canon])
        })

    # Group dihedral orbits under G_macro = <mu_2> (order 3)
    p_to_orbit_idx = {}
    for idx, o in enumerate(d_orbits):
        for p in o["members"]:
            p_to_orbit_idx[p] = idx

    visited_macro = set()
    macro_orbits = []
    for idx, o in enumerate(d_orbits):
        if idx in visited_macro:
            continue
        p = o["canon"]
        # Cycle under mu_2
        cycle_indices = []
        curr = p
        for step in range(3):
            # Find orbit index of curr
            curr_canon = partition_canonical(curr, 9)
            o_idx = p_to_orbit_idx[curr_canon]
            if o_idx not in cycle_indices:
                cycle_indices.append(o_idx)
            # dilate by 2
            curr = tuple(sorted([tuple(sorted([(2 * x) % 9 for x in blk])) for blk in curr]))

        visited_macro.update(cycle_indices)
        macro_orbits.append({
            "size": len(cycle_indices),
            "orbit_indices": cycle_indices,
            "d_orbits": [d_orbits[i] for i in cycle_indices]
        })

    # Separate monomers and trimers
    monomers = [m for m in macro_orbits if m["size"] == 1]
    trimers = [m for m in macro_orbits if m["size"] == 3]

    # For each trimer, find its canonical representative
    # The representative of the trimer should be the lexicographical minimum of the 3 member dihedral canonical reps!
    processed_trimers = []
    for t in trimers:
        # Find the canonical rep among the 3 orbits
        sorted_orbits = sorted(t["d_orbits"], key=lambda o: o["canon"])
        head_orbit = sorted_orbits[0]
        p1 = head_orbit["canon"]
        p2 = tuple(sorted([tuple(sorted([(2 * x) % 9 for x in blk])) for blk in p1]))
        p3 = tuple(sorted([tuple(sorted([(2 * x) % 9 for x in blk])) for blk in p2]))

        processed_trimers.append({
            "head_canon": p1,
            "strip": (p1, p2, p3),
            "size": head_orbit["size"],
            "s": head_orbit["s"],
            "E": head_orbit["E"],
            "strides": head_orbit["strides"],
        })

    # Sort trimers by 5-tier cascade:
    # 1. |O| ascending
    # 2. s descending
    # 3. E descending
    # 4. strides
    # 5. head_canon lexicographically
    sorted_trimers = sorted(processed_trimers, key=lambda t: (
        t["size"],
        -t["s"],
        -t["E"],
        t["strides"],
        t["head_canon"]
    ))

    print(f"=== STRICT 5-TIER CASCADE FOR D_9 TRIMERS ===")
    for idx, t in enumerate(sorted_trimers, 1):
        p1, p2, p3 = t["strip"]
        print(f"T{idx}: |O|={t['size']} s={t['s']} E={t['E']} strides={t['strides']}")
        print(f"   mu_1: {p_to_str(p1)}")
        print(f"   mu_2: {p_to_str(p2)}")
        print(f"   mu_4: {p_to_str(p3)}")

    # Now compare with what was in generate_small_universes.py
    print("\n=== CURRENT generate_small_universes.py TRIMERS ===")
    from hexdec.tools.generate_small_universes import generate_d9_tikz
    # Let's read the list directly
    import re
    with open("hexdec/tools/generate_small_universes.py") as f:
        src = f.read()
    # Extract trimers lines
    for line in src.splitlines():
        if "# T" in line and "|O|=" in line:
            print(line.strip())

if __name__ == "__main__":
    full_d9_census()
