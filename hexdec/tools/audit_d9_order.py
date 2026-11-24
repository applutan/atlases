#!/usr/bin/env python3
"""
audit_d9_order.py - Audit the sorting of D_9 trimers against the 5-tier cascade.

Author: Gemma Knee
"""

import math
from typing import List, Tuple

def get_cyclic_strides(block, n):
    sb = sorted(list(block))
    L = len(sb)
    strides = []
    for i in range(L):
        d = (sb[(i + 1) % L] - sb[i]) % n
        strides.append(d)
    # unoriented canonical stride: min over cyclic shifts and reversals
    candidates = []
    for i in range(L):
        shift = strides[i:] + strides[:i]
        candidates.append(tuple(shift))
        rev = list(reversed(shift))
        rev = rev[-1:] + rev[:-1] # cyclic match
        candidates.append(tuple(rev))
    return min(candidates)

def is_block_symmetric(block, n):
    sb = sorted(list(block))
    for c in range(n):
        ref_b = sorted([(-x + c) % n for x in sb])
        if ref_b == sb:
            return True
    return False

def compute_chord_energy(blocks, n):
    total = 0
    for blk in blocks:
        sb = sorted(list(blk))
        L = len(sb)
        for i in range(L):
            for j in range(i + 1, L):
                d = min((sb[j] - sb[i]) % n, (sb[i] - sb[j]) % n)
                total += d * d
    return total

def analyze_trimers():
    # Load raw trimers from generate_small_universes.py
    trimers = [
        ("T1", [[0, 1, 5], [2, 6, 7], [3, 4, 8]], 3),
        ("T2", [[0, 1, 5], [2, 3, 7], [4, 6, 8]], 9),
        ("T3", [[0, 1, 5], [2, 4, 7], [3, 6, 8]], 9),
        ("T4", [[0, 1, 4], [2, 5, 6], [3, 7, 8]], 9),
        ("T5", [[0, 2, 5], [1, 4, 7], [3, 6, 8]], 9),
        ("T6", [[0, 1, 4], [2, 6, 7], [3, 5, 8]], 18),
        ("T7", [[0, 1, 4], [2, 6, 8], [3, 5, 7]], 18),
        ("T8", [[0, 1, 4], [2, 5, 7], [3, 6, 8]], 18),
    ]

    print(f"{'Trimer':<8} {'|O|':<5} {'s':<4} {'E':<5} {'Strides':<35} {'Blocks'}")
    print("-" * 80)
    for name, p, sz in trimers:
        s_count = sum(1 for b in p if is_block_symmetric(b, 9))
        E = compute_chord_energy(p, 9)
        strides = sorted([get_cyclic_strides(b, 9) for b in p])
        strides_str = ", ".join(str(st) for st in strides)
        p_str = "/" + "/".join("".join(str(x) for x in b) for b in p) + "/"
        print(f"{name:<8} {sz:<5} {s_count:<4} {E:<5} {strides_str:<35} {p_str}")

if __name__ == "__main__":
    analyze_trimers()
