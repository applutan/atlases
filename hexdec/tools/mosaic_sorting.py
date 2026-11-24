#!/usr/bin/env python3
"""
mosaic_sorting.py - Natural Geometric Sorting Cascade for Composition Mosaics

Hierarchy:
1. Dihedral Orbit Size |O| (ascending: 1 -> 2 -> 4 -> 8 -> 16 -> 32)
2. Symmetric Block Count s (descending: 4 -> 3 -> 2 -> 1 -> 0, blue-to-pink visual gradient)
3. Chord Dispersion Energy E(P) (descending: high energy/regular -> low energy/clustered)
4. Canonical Stride Profile Multiset (canonical tuple of unoriented cyclic strides)
5. Canonical Lexicographic Representation
"""

import math
from typing import List, Tuple

def is_block_symmetric(block, n=16) -> bool:
    sb = sorted(list(block))
    for c in range(n):
        ref_b = sorted([(-x + c) % n for x in sb])
        if ref_b == sb:
            return True
    return False

def get_block_canonical_stride(block, n=16) -> Tuple[int, ...]:
    sb = sorted(list(block))
    L = len(sb)
    if L <= 1:
        return (n,)
    strides = [((sb[(i + 1) % L] - sb[i]) % n) for i in range(L)]
    # Min under cyclic shift and reflection
    cycles = []
    for shift in range(L):
        c = strides[shift:] + strides[:shift]
        cycles.append(tuple(c))
        cycles.append(tuple(reversed(c)))
    return min(cycles)

def compute_mosaic_chord_energy(blocks, n=16) -> int:
    """Sum of squared circular chord distances across all blocks."""
    total_energy = 0
    for blk in blocks:
        sb = sorted(list(blk))
        L = len(sb)
        for i in range(L):
            for j in range(i + 1, L):
                d = min((sb[j] - sb[i]) % n, (sb[i] - sb[j]) % n)
                total_energy += d * d
    return total_energy

def get_chirality_signature(partition, n=16) -> str:
    """
    Return a 4-character signature (e.g. 'ssss', 'ssnn', 'nnnn')
    indicating reflectional symmetry ('s') vs chirality ('n') for each
    block in canonical block order (sorted by minimum element).
    """
    s_blocks = sorted([sorted(list(b)) for b in partition])
    return "".join("s" if is_block_symmetric(b, n) else "n" for b in s_blocks)

def get_mosaic_sort_key(p, orb_size: int, n=16):
    """
    Compute the natural sorting key for partition p with dihedral orbit size orb_size.
    Key tuple:
      (orb_size, -s, -energy, stride_profile_tuple, canonical_blocks)
    """
    s_blocks = [sorted(list(b)) for b in p]
    s_blocks.sort(key=lambda b: (min(b), b))
    
    # Invariant 2: Symmetric block count s (negated for descending sort)
    s = sum(1 for b in s_blocks if is_block_symmetric(b, n))
    
    # Invariant 3: Chord energy E (negated for descending sort)
    energy = compute_mosaic_chord_energy(s_blocks, n)
    
    # Invariant 4: Canonical stride profile multiset
    strides = tuple(sorted(get_block_canonical_stride(b, n) for b in s_blocks))
    
    # Invariant 5: Lexicographical tie-breaker
    canon_blocks = tuple(tuple(b) for b in s_blocks)
    
    return (orb_size, -s, -energy, strides, canon_blocks)
