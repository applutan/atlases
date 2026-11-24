#!/usr/bin/env python3
"""
d9_tiered_census.py - Compute D_9 Trimers using the exact same 5-tier natural sorting cascade
and candidate cycle selection as used for the Z_16 tetramers.

Author: Gemma Knee
"""

import math
import itertools

def get_block_canonical_stride(block, n=9):
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

def compute_mosaic_chord_energy(blocks, n=9):
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

def get_chirality_sig(p, n=9):
    return "".join("s" if is_block_symmetric(b, n) else "n" for b in p)

def compute_d9_tiered():
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

    # Dihedral orbits
    d_group = [(a, b) for a in [1, -1] for b in range(9)]
    visited = set()
    d_orbits = {}
    for p in raw_set:
        if p in visited:
            continue
        orbit = frozenset(tuple(sorted([tuple(sorted([(a * x + b) % 9 for x in blk])) for blk in p])) for a, b in d_group)
        visited.update(orbit)
        d_orbits[orbit] = len(orbit)

    visited_orbs = set()
    monomers = []
    trimers = []

    for o, sz in d_orbits.items():
        if o in visited_orbs:
            continue
        rep = sorted(list(o), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        # dilate by 2
        rep_mu2 = tuple(sorted([tuple(sorted([(2 * x) % 9 for x in blk])) for blk in rep]))
        o2 = frozenset(tuple(sorted([tuple(sorted([(a * x + b) % 9 for x in blk])) for blk in rep_mu2])) for a, b in d_group)

        if o2 == o:
            visited_orbs.add(o)
            # Monomer
            s_cnt = sum(1 for b in rep if is_block_symmetric(b, 9))
            e = compute_mosaic_chord_energy(rep, 9)
            strides = tuple(sorted(get_block_canonical_stride(b, 9) for b in rep))
            key = (sz, -s_cnt, -e, strides, rep)
            monomers.append((key, rep, sz))
            continue

        rep_mu4 = tuple(sorted([tuple(sorted([(2 * x) % 9 for x in blk])) for blk in rep_mu2]))
        o3 = frozenset(tuple(sorted([tuple(sorted([(a * x + b) % 9 for x in blk])) for blk in rep_mu4])) for a, b in d_group)

        visited_orbs.add(o)
        visited_orbs.add(o2)
        visited_orbs.add(o3)

        # Trimer: test all 3 candidate orbits as head of the strip
        candidate_cycles = []
        for cand_o in [o, o2, o3]:
            c_rep = sorted(list(cand_o), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
            cp1 = [sorted(list(b)) for b in c_rep]
            cp2 = sorted([sorted([(2 * x) % 9 for x in b]) for b in cp1])
            cp3 = sorted([sorted([(4 * x) % 9 for x in b]) for b in cp1])

            s_cnt = sum(1 for b in cp1 if is_block_symmetric(b, 9))
            e = compute_mosaic_chord_energy(cp1, 9)
            strides = tuple(sorted(get_block_canonical_stride(b, 9) for b in cp1))
            # Sort key matching 5-tier cascade:
            # Tier 1: sz ascending
            # Tier 2: s_cnt descending (-s_cnt)
            # Tier 3: e descending (-e)
            # Tier 4: strides
            # Tier 5: lexicographical partition
            key = (sz, -s_cnt, -e, strides, tuple(tuple(b) for b in cp1))
            candidate_cycles.append((key, (cp1, cp2, cp3), sz))

        candidate_cycles.sort(key=lambda x: x[0])
        best_cycle = candidate_cycles[0]
        trimers.append(best_cycle)

    trimers.sort(key=lambda x: x[0])

    print("=== TIERED D_9 MONOMER ===")
    for key, rep, sz in monomers:
        s_cnt = -key[1]
        e = -key[2]
        print(f"M1: |O|={sz} s={s_cnt} E={e} {p_to_str(rep)} [{get_chirality_sig(rep)}]")

    print("\n=== TIERED D_9 TRIMERS (Strict 5-Tier Cascade with Best Candidate Head) ===")
    for idx, (key, cycle, sz) in enumerate(trimers, 1):
        p1, p2, p3 = cycle
        s_cnt = -key[1]
        e = -key[2]
        sig1 = get_chirality_sig(p1)
        sig2 = get_chirality_sig(p2)
        sig3 = get_chirality_sig(p3)
        strides = key[3]
        print(f"T{idx}: |O|={sz:<2d} s={s_cnt} E={e:<2d} {p_to_str(p1)} [{sig1}] -> {p_to_str(p2)} [{sig2}] -> {p_to_str(p3)} [{sig3}]")
        print(f"    Strides: {strides}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compute D_9 Trimers using the exact 5-tier natural sorting cascade.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print detailed decomposition steps")
    args = parser.parse_args()
    compute_d9_tiered()
