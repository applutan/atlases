#!/usr/bin/env python3
"""
estimate_pages_up_to_16.py

Calculates exact dihedral and cyclic orbit counts for circular rings Z_3 to Z_16,
and models the exact page count required for visual plates under current layout rules:
- 6 drawings per row (cols = 6)
- Ring initial page (with section heading): up to 8 rows (48 orbits)
- Ring continuation pages: up to 9 rows (54 orbits)

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import math
import sys

def euler_phi(n):
    return sum(1 for i in range(1, n + 1) if math.gcd(n, i) == 1)

def count_dihedral_bracelets(n, k):
    """Exact Burnside count of k-subsets of Z_n under D_n."""
    divs = [d for d in range(1, n + 1) if n % d == 0]
    rot_sum = 0
    for d in divs:
        if k % d == 0:
            rot_sum += euler_phi(d) * math.comb(n // d, k // d)

    refl_sum = 0
    if n % 2 == 1:
        m = (n - 1) // 2
        refl_sum = n * math.comb(m, k // 2)
    else:
        m = n // 2
        # m vertex-vertex axes (each fixes 2 vertices, m-1 pairs)
        # m edge-edge axes (each fixes 0 vertices, m pairs)
        if k % 2 == 0:
            vv_count = math.comb(m - 1, k // 2) + math.comb(m - 1, (k - 2) // 2) if k >= 2 else math.comb(m - 1, 0)
            ee_count = math.comb(m, k // 2)
            refl_sum = m * vv_count + m * ee_count
        else:
            vv_count = 2 * math.comb(m - 1, (k - 1) // 2)
            ee_count = 0
            refl_sum = m * vv_count

    return (rot_sum + refl_sum) // (2 * n)

def count_cyclic_necklaces(n, k):
    """Exact Burnside count of k-subsets of Z_n under C_n."""
    divs = [d for d in range(1, n + 1) if n % d == 0]
    rot_sum = 0
    for d in divs:
        if k % d == 0:
            rot_sum += euler_phi(d) * math.comb(n // d, k // d)
    return rot_sum // n

def model_pages_for_ring(orbits_count, cols=6, max_first=8, max_cont=9):
    """Computes exact pages for a ring starting on a fresh page."""
    first_cap = max_first * cols # 48
    cont_cap = max_cont * cols   # 54
    if orbits_count <= first_cap:
        return 1
    rem = orbits_count - first_cap
    cont_pages = math.ceil(rem / cont_cap)
    return 1 + cont_pages

def main():
    cols = 6
    print("=" * 85)
    print(f"{'Ring':<6} | {'Subsets':<10} | {'Dihedral':<10} | {'Cyclic':<10} | {'Chiral %':<9} | {'Rows':<6} | {'Atlas Pages':<12}")
    print("=" * 85)

    cumulative_dihedral = 0
    atlas_pages_by_ring = {}

    for n in range(3, 17):
        d_tot = sum(count_dihedral_bracelets(n, k) for k in range(n + 1))
        c_tot = sum(count_cyclic_necklaces(n, k) for k in range(n + 1))
        chiral_pairs = c_tot - d_tot
        pct = (chiral_pairs / d_tot) * 100.0 if d_tot > 0 else 0.0
        rows = math.ceil(d_tot / cols)

        if n in [3, 4, 5]:
            # Shared on 1 page
            p_desc = "shared p.1"
            atlas_pages_by_ring[n] = 1/3 # representative
        elif n in [6, 7]:
            # Shared on 1 page
            p_desc = "shared p.2"
            atlas_pages_by_ring[n] = 1/2
        elif n == 8:
            p_desc = "1 page (p.3)"
            atlas_pages_by_ring[n] = 1
        elif n == 9:
            p_desc = "1 page (p.4)"
            atlas_pages_by_ring[n] = 1
        else:
            pages = model_pages_for_ring(d_tot, cols, 8, 9)
            p_desc = f"{pages} pages"
            atlas_pages_by_ring[n] = pages

        cumulative_dihedral += d_tot
        print(f"Z_{n:<4} | {2**n:<10,d} | {d_tot:<10,d} | {c_tot:<10,d} | {pct:<8.1f}% | {rows:<6} | {p_desc:<12}")

    print("=" * 85)
    
    # Summary of Atlas Page Growth
    print("\nATLAS PAGE SCENARIOS:")
    print("-" * 55)
    base_front_back = 6 # Preface (2), ToC (2), Chap 1 & 2 (4) - some roman
    # Up to Z_12:
    p_z12 = 1 + 1 + 1 + 1 + model_pages_for_ring(78) + model_pages_for_ring(126) + model_pages_for_ring(224)
    print(f"Visual Atlas pages for Z_3..Z_12: {p_z12} pages (Total monograph: ~25 pages)")

    p_z13 = p_z12 + model_pages_for_ring(sum(count_dihedral_bracelets(13, k) for k in range(14)))
    d_13 = sum(count_dihedral_bracelets(13, k) for k in range(14))
    print(f"Adding Z_13 ({d_13} orbits): +{model_pages_for_ring(d_13)} pages -> {p_z13} atlas pages")

    p_z14 = p_z13 + model_pages_for_ring(sum(count_dihedral_bracelets(14, k) for k in range(15)))
    d_14 = sum(count_dihedral_bracelets(14, k) for k in range(15))
    print(f"Adding Z_14 ({d_14} orbits): +{model_pages_for_ring(d_14)} pages -> {p_z14} atlas pages")

    p_z15 = p_z14 + model_pages_for_ring(sum(count_dihedral_bracelets(15, k) for k in range(16)))
    d_15 = sum(count_dihedral_bracelets(15, k) for k in range(16))
    print(f"Adding Z_15 ({d_15} orbits): +{model_pages_for_ring(d_15)} pages -> {p_z15} atlas pages")

    p_z16 = p_z15 + model_pages_for_ring(sum(count_dihedral_bracelets(16, k) for k in range(17)))
    d_16 = sum(count_dihedral_bracelets(16, k) for k in range(17))
    print(f"Adding Z_16 ({d_16} orbits): +{model_pages_for_ring(d_16)} pages -> {p_z16} atlas pages")

    tot_16_orbits = sum(sum(count_dihedral_bracelets(n, k) for k in range(n + 1)) for n in range(3, 17))
    print(f"\nGrand Total Dihedral Orbits for Z_3..Z_16: {tot_16_orbits:,d} orbits")
    print(f"Total Visual Atlas pages for Z_3..Z_16: {p_z16} pages")
    print(f"Estimated Total Monograph pages for Z_3..Z_16: ~{p_z16 + 8} pages")

if __name__ == "__main__":
    main()
