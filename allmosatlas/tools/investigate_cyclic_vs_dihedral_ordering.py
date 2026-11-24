#!/usr/bin/env python3
"""
investigate_cyclic_vs_dihedral_ordering.py

Investigates the structural and ordering relationship between:
1. Dihedral orbits (D_8, order 16) - the 354 mosaics of the current atlas.
2. Cyclic orbits (C_8, order 8) - the rotational-only classification.

Addresses two key questions:
1. Would a cyclic-group-based catalogue have its mosaics ordered in roughly the same positions?
2. Are chiral enantiomorphic pairs placed "close by" or "next door" in the cyclic catalogue,
   or does canonical lexicographical string minimization separate them?

Usage:
    python3 investigate_cyclic_vs_dihedral_ordering.py [--verbose] [--output report.md]
"""

import sys
import argparse
from collections import defaultdict

def get_partitions(elements):
    """Generate all set partitions of a given list of elements."""
    if not elements:
        yield []
        return
    first = elements[0]
    rest = elements[1:]
    for smaller in get_partitions(rest):
        for i, block in enumerate(smaller):
            yield smaller[:i] + [sorted([first] + block)] + smaller[i+1:]
        yield [[first]] + smaller

def is_block_symmetric(block, n=8):
    """Check if a block is invariant under some reflection in D_n."""
    b_set = set(block)
    for c in range(n):
        refl = {(c - x) % n for x in b_set}
        if refl == b_set:
            return True
    return False

def compute_block_energy(block, n=8):
    """Compute sum of squared circular chord distances."""
    e = 0
    m = len(block)
    for i in range(m):
        for j in range(i + 1, m):
            d = min((block[j] - block[i]) % n, (block[i] - block[j]) % n)
            e += d * d
    return e

def canonicalise_partition_d8(part, n=8):
    """Find canonical representative under D_n (rotations and reflections)."""
    d8_ops = [(a, b) for a in [1, n - 1] for b in range(n)]
    best = None
    for a, b in d8_ops:
        cand = [sorted((a * x + b) % n for x in blk) for blk in part]
        cand.sort(key=lambda blk: (min(blk), blk))
        cand_tuple = tuple(tuple(blk) for blk in cand)
        if best is None or cand_tuple < best:
            best = cand_tuple
    return [list(blk) for blk in best]

def canonicalise_partition_c8(part, n=8):
    """Find canonical representative under C_n (rotations only)."""
    c8_ops = [(1, b) for b in range(n)]
    best = None
    for a, b in c8_ops:
        cand = [sorted((a * x + b) % n for x in blk) for blk in part]
        cand.sort(key=lambda blk: (min(blk), blk))
        cand_tuple = tuple(tuple(blk) for blk in cand)
        if best is None or cand_tuple < best:
            best = cand_tuple
    return [list(blk) for blk in best]

def get_orbit_d8(part, n=8):
    """Get all distinct partitions in the D_n orbit."""
    d8_ops = [(a, b) for a in [1, n - 1] for b in range(n)]
    orb = set()
    for a, b in d8_ops:
        cand = [sorted((a * x + b) % n for x in blk) for blk in part]
        cand.sort(key=lambda blk: (min(blk), blk))
        cand_tuple = tuple(tuple(blk) for blk in cand)
        orb.add(cand_tuple)
    return orb

def get_orbit_c8(part, n=8):
    """Get all distinct partitions in the C_n orbit."""
    c8_ops = [(1, b) for b in range(n)]
    orb = set()
    for a, b in c8_ops:
        cand = [sorted((a * x + b) % n for x in blk) for blk in part]
        cand.sort(key=lambda blk: (min(blk), blk))
        cand_tuple = tuple(tuple(blk) for blk in cand)
        orb.add(cand_tuple)
    return orb

def has_reflection_symmetry(part, n=8):
    """Check if the partition as a whole is invariant under some reflection."""
    norm_part = set(tuple(sorted(b)) for b in part)
    for c in range(n):
        # reflection x -> (c - x) % n
        refl_part = set(tuple(sorted((c - x) % n for x in b)) for b in part)
        if refl_part == norm_part:
            return True
    return False

def reflect_partition(part, n=8):
    """Reflect partition across x -> -x % n."""
    refl = [sorted((n - x) % n for x in b) for b in part]
    refl.sort(key=lambda blk: (min(blk), blk))
    return refl

def format_slash(part):
    """Format partition in hexadecimal slash notation."""
    blocks_str = []
    for blk in part:
        s = "".join(f"{x:X}" for x in blk)
        blocks_str.append(s)
    return "/" + "/".join(blocks_str) + "/"

def main():
    parser = argparse.ArgumentParser(
        description="Investigate ordering properties of Cyclic (C_8) vs Dihedral (D_8) Mosaic Catalogues."
    )
    parser.add_argument("--verbose", action="store_true", help="Print detailed per-orbit diagnostics.")
    parser.add_argument("--output", type=str, default=None, help="Optional Markdown report output path.")
    args = parser.parse_args()

    n = 8
    raw_partitions = list(get_partitions(list(range(n))))
    total_raw = len(raw_partitions)

    # Group raw partitions by shape
    shapes_dict = defaultdict(list)
    for p in raw_partitions:
        p_norm = [sorted(b) for b in p]
        p_norm.sort(key=lambda blk: (min(blk), blk))
        shape = tuple(sorted([len(b) for b in p_norm], reverse=True))
        shapes_dict[shape].append(p_norm)

    sorted_shapes = sorted(shapes_dict.keys(), key=lambda sh: (len(sh), [-x for x in sh]))

    # Compute D_8 catalogue
    d8_catalogue = []
    c8_catalogue = []

    # Map partition tuple to D_8 orbit ID
    part_to_d8_id = {}

    d8_global_id = 1
    c8_global_id = 1

    chiral_d8_orbits = []
    achiral_d8_orbits = []

    # Process D_8 first
    for shape in sorted_shapes:
        raw_list = shapes_dict[shape]
        seen_d8 = set()
        shape_d8_orbits = []

        for p in raw_list:
            canon = canonicalise_partition_d8(p, n)
            canon_tup = tuple(tuple(b) for b in canon)
            if canon_tup not in seen_d8:
                seen_d8.add(canon_tup)
                orb = get_orbit_d8(canon, n)
                orb_sz = len(orb)
                is_achiral_mosaic = has_reflection_symmetry(canon, n)
                s_count = sum(1 for b in canon if is_block_symmetric(b, n))
                sig = "".join("s" if is_block_symmetric(b, n) else "c" for b in canon)
                energy = sum(compute_block_energy(b, n) for b in canon)

                shape_d8_orbits.append({
                    'shape': shape,
                    'partition': canon,
                    'slash': format_slash(canon),
                    'orbit_size': orb_sz,
                    'stab_size': 16 // orb_sz,
                    's_count': s_count,
                    'sig': sig,
                    'energy': energy,
                    'is_achiral': is_achiral_mosaic,
                    'raw_members': orb,
                })

        # Sort D_8 orbits within shape by the canonical cascade:
        # (-s_count, -energy, slash)
        shape_d8_orbits.sort(key=lambda o: (-o['s_count'], -o['energy'], o['slash']))
        for o in shape_d8_orbits:
            o['global_id'] = d8_global_id
            d8_global_id += 1
            d8_catalogue.append(o)
            for mem in o['raw_members']:
                part_to_d8_id[mem] = o['global_id']
            if o['is_achiral']:
                achiral_d8_orbits.append(o)
            else:
                chiral_d8_orbits.append(o)

    # Process C_8 catalogue using identical sorting cascade:
    # 1. Part count s
    # 2. Shape lambda
    # 3. Intra-shape: (-s_count, -energy, C_8 canonical slash)
    c8_orbits_by_d8 = defaultdict(list)

    for shape in sorted_shapes:
        raw_list = shapes_dict[shape]
        seen_c8 = set()
        shape_c8_orbits = []

        for p in raw_list:
            canon = canonicalise_partition_c8(p, n)
            canon_tup = tuple(tuple(b) for b in canon)
            if canon_tup not in seen_c8:
                seen_c8.add(canon_tup)
                orb = get_orbit_c8(canon, n)
                orb_sz = len(orb)
                s_count = sum(1 for b in canon if is_block_symmetric(b, n))
                sig = "".join("s" if is_block_symmetric(b, n) else "c" for b in canon)
                energy = sum(compute_block_energy(b, n) for b in canon)
                parent_d8_id = part_to_d8_id[canon_tup]

                shape_c8_orbits.append({
                    'shape': shape,
                    'partition': canon,
                    'slash': format_slash(canon),
                    'orbit_size': orb_sz,
                    'stab_size': 8 // orb_sz,
                    's_count': s_count,
                    'sig': sig,
                    'energy': energy,
                    'parent_d8_id': parent_d8_id,
                    'raw_members': orb,
                })

        shape_c8_orbits.sort(key=lambda o: (-o['s_count'], -o['energy'], o['slash']))
        for o in shape_c8_orbits:
            o['global_id'] = c8_global_id
            c8_global_id += 1
            c8_catalogue.append(o)
            c8_orbits_by_d8[o['parent_d8_id']].append(o)

    total_d8 = len(d8_catalogue)
    total_c8 = len(c8_catalogue)
    num_achiral = len(achiral_d8_orbits)
    num_chiral = len(chiral_d8_orbits)

    # Analyze chiral pairs in C_8 catalogue
    enantiomorph_distances = []
    adjacent_count = 0
    close_count_le_3 = 0
    far_count = 0

    for d8_id, c8_list in c8_orbits_by_d8.items():
        if len(c8_list) == 2:
            idx1 = c8_list[0]['global_id']
            idx2 = c8_list[1]['global_id']
            dist = abs(idx2 - idx1)
            enantiomorph_distances.append({
                'd8_id': d8_id,
                'shape': c8_list[0]['shape'],
                'c8_id1': idx1,
                'c8_id2': idx2,
                'slash1': c8_list[0]['slash'],
                'slash2': c8_list[1]['slash'],
                'energy': c8_list[0]['energy'],
                's_count': c8_list[0]['s_count'],
                'distance': dist,
            })
            if dist == 1:
                adjacent_count += 1
            if dist <= 3:
                close_count_le_3 += 1
            else:
                far_count += 1

    # Relative rank correlation between D_8 ID and primary C_8 ID
    d8_ranks = []
    c8_ranks = []
    rank_shifts = []

    for o_d8 in d8_catalogue:
        d8_id = o_d8['global_id']
        c8_list = c8_orbits_by_d8[d8_id]
        c8_primary_id = c8_list[0]['global_id']
        # Normalized positions in [0, 1]
        norm_d8 = (d8_id - 1) / (total_d8 - 1)
        norm_c8 = (c8_primary_id - 1) / (total_c8 - 1)
        d8_ranks.append(norm_d8)
        c8_ranks.append(norm_c8)
        rank_shifts.append(abs(norm_c8 - norm_d8))

    max_shift = max(rank_shifts)
    mean_shift = sum(rank_shifts) / len(rank_shifts)

    print("=" * 80)
    print("CYCLIC (C_8) VS DIHEDRAL (D_8) MOSAIC CATALOGUE COMPARISON")
    print("=" * 80)
    print(f"Total Bell Partitions B_8:            {total_raw}")
    print(f"Total Dihedral (D_8) Mosaic Orbits:   {total_d8} (Table B.8)")
    print(f"  - Achiral D_8 orbits (reflectional): {num_achiral} ({num_achiral/total_d8*100:.1f}%)")
    print(f"  - Chiral D_8 orbits (enantiomorphic):{num_chiral} ({num_chiral/total_d8*100:.1f}%)")
    print(f"Total Cyclic (C_8) Mosaic Orbits:     {total_c8}")
    print(f"  Calculation: {num_achiral} (achiral) + 2 x {num_chiral} (chiral) = {num_achiral + 2 * num_chiral} = {total_c8}")
    print("-" * 80)
    print("QUESTION 1: Are mosaics ordered in roughly the same positions?")
    print(f"  Mean relative position shift:       {mean_shift * 100:.2f}% of the catalogue length")
    print(f"  Max relative position shift:        {max_shift * 100:.2f}% of the catalogue length")
    print("  -> YES: Because Tier 1 (stratum s) and Tier 2 (shape lambda) partition both")
    print("     catalogues into the exact same blocks in the exact same sequence,")
    print("     every mosaic stays in its identical shape cluster!")
    print("-" * 80)
    print("QUESTION 2: Are chiral enantiomorphic pairs 'next door' or close by?")
    print(f"  Total Chiral Pairs in C_8:          {len(enantiomorph_distances)}")
    print(f"  Strictly Adjacent (dist = 1, next door): {adjacent_count} / {len(enantiomorph_distances)} ({adjacent_count/len(enantiomorph_distances)*100:.1f}%)")
    print(f"  Close by (dist <= 3):                {close_count_le_3} / {len(enantiomorph_distances)} ({close_count_le_3/len(enantiomorph_distances)*100:.1f}%)")
    print(f"  Separated (dist > 3):                {far_count} / {len(enantiomorph_distances)} ({far_count/len(enantiomorph_distances)*100:.1f}%)")
    print(f"  Max distance between enantiomorphs:  {max(d['distance'] for d in enantiomorph_distances)}")
    print("-" * 80)

    # Inspect some examples of adjacent vs separated
    print("\nSample Enantiomorphic Pairs in C_8 Catalogue:")
    print("-------------------------------------------------------------------------------")
    print(" D8_ID  Shape        C8_IDs     Dist  Energy  Sig     Slash 1        Slash 2")
    print("-------------------------------------------------------------------------------")
    for d in enantiomorph_distances[:15]:
        sh_str = "(" + ",".join(str(x) for x in d['shape']) + ")"
        print(f" {d['d8_id']:5d}  {sh_str:<12} {d['c8_id1']:3d}, {d['c8_id2']:3d}   {d['distance']:3d}   {d['energy']:5d}   {d['s_count']}    {d['slash1']:<14} {d['slash2']:<14}")

    # Inspect the most separated pairs
    sorted_by_dist = sorted(enantiomorph_distances, key=lambda x: -x['distance'])
    print("\nMost Separated Enantiomorphic Pairs in C_8 Catalogue:")
    print("-------------------------------------------------------------------------------")
    print(" D8_ID  Shape        C8_IDs     Dist  Energy  Sig     Slash 1        Slash 2")
    print("-------------------------------------------------------------------------------")
    for d in sorted_by_dist[:10]:
        sh_str = "(" + ",".join(str(x) for x in d['shape']) + ")"
        print(f" {d['d8_id']:5d}  {sh_str:<12} {d['c8_id1']:3d}, {d['c8_id2']:3d}   {d['distance']:3d}   {d['energy']:5d}   {d['s_count']}    {d['slash1']:<14} {d['slash2']:<14}")

    # Check our friend at 227 (unique cyclic Skolem sequence)
    # Shape z_2^4, slash /01/25/37/46/
    o227_d8 = d8_catalogue[226] # 0-indexed
    print("\nOur Friend at Orbit 227:")
    print(f"  D_8 Orbit 227: Shape {o227_d8['shape']}, Slash {o227_d8['slash']}, Achiral? {o227_d8['is_achiral']}, Orbit Size |O|={o227_d8['orbit_size']}")
    c8_for_227 = c8_orbits_by_d8[227]
    print(f"  C_8 representation count: {len(c8_for_227)}")
    for c in c8_for_227:
        print(f"    C_8 Orbit {c['global_id']}: Slash {c['slash']}, Orbit Size {c['orbit_size']}, |Stab|={c['stab_size']}")

if __name__ == "__main__":
    main()
