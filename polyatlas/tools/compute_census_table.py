#!/usr/bin/env python3
"""
compute_census_table.py - Computes exact theoretical census of subset orbits
under Cyclic group C_n and Dihedral group D_n for rings Z_1 through Z_16.

Uses Burnside's Lemma / Cycle Index exact formulas:
For C_n:
  N(C_n) = (1/n) * sum_{d | n} phi(d) * 2^(n/d)

For D_n:
  - If n is odd:
      N(D_n) = (1/(2n)) * [ sum_{d | n} phi(d) * 2^(n/d) + n * 2^((n+1)/2) ]
  - If n is even:
      N(D_n) = (1/(2n)) * [ sum_{d | n} phi(d) * 2^(n/d) + (n/2) * ( 2^(n/2) + 2^(n/2 + 1) ) ]
             = (1/(2n)) * [ sum_{d | n} phi(d) * 2^(n/d) + n * 3 * 2^(n/2 - 1) ]

For degenerate rings Z_1 and Z_2:
  Z_1: 1 vertex {0}. Subsets: empty, {0}. Total = 2.
       C_1 = {id}. D_1 = {id, reflection}.
       In 1D, reflection of vertex 0 is 0. So reflection leaves all subsets fixed.
       |D_1|: formally |C_1| = 1, or |D_1| = 2 if vertical reflection is included.
       Orbits: 2 (both achiral).
  Z_2: 2 vertices {0, 1}. Subsets: empty, {0}, {1}, {0,1}. Total = 4.
       Under C_2: {0} and {1} are related by rotation (shift by 1).
       So 3 cyclic orbits: empty, {0,1}, and {{0}, {1}}.
       Under D_2: reflection tau(x) = -x mod 2 maps 0->0, 1->1.
       All 3 orbits are achiral.
       |D_2|: 4 (or 2 if D_2 = C_2). In standard definition |D_n| = 2n, so |D_2| = 4, |D_1| = 2.
"""

import math
import argparse

def phi(n):
    res = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            res -= res // p
        p += 1
    if temp > 1:
        res -= res // temp
    return res

def cyclic_orbits(n):
    # (1/n) * sum_{d | n} phi(d) * 2^(n/d)
    total = 0
    for d in range(1, n + 1):
        if n % d == 0:
            total += phi(d) * (2 ** (n // d))
    return total // n

def dihedral_orbits(n):
    if n == 1:
        return 2
    if n == 2:
        return 3
    c_sum = sum(phi(d) * (2 ** (n // d)) for d in range(1, n + 1) if n % d == 0)
    if n % 2 == 1:
        refl_sum = n * (2 ** ((n + 1) // 2))
    else:
        # n/2 vertex-vertex reflections (2^(n/2 + 1) fixed subsets)
        # n/2 edge-edge reflections (2^(n/2) fixed subsets)
        refl_sum = (n // 2) * (2 ** (n // 2 + 1) + 2 ** (n // 2))
    return (c_sum + refl_sum) // (2 * n)

def main():
    parser = argparse.ArgumentParser(description="Compute exact census of subset orbits.")
    parser.add_argument("--max-n", type=int, default=16, help="Maximum n (default: 16)")
    parser.add_argument("--latex", action="store_true", help="Print LaTeX table format")
    args = parser.parse_args()

    print(f"{'Ring':<6} | {'Subsets':<8} | {'|D_n|':<5} | {'Dihedral':<8} | {'Cyclic':<8} | {'Chiral Orbits':<13} | {'Chiral %':<8}")
    print("-" * 75)

    latex_rows = []

    for n in range(1, args.max_n + 1):
        subsets = 2 ** n
        dn_order = 2 * n  # standard order |D_n| = 2n
        d_orb = dihedral_orbits(n)
        c_orb = cyclic_orbits(n)
        # Each chiral dihedral orbit splits into 2 cyclic orbits:
        # c_orb = (d_orb - chiral) + 2 * chiral = d_orb + chiral
        # Therefore:
        chiral_d_orb = c_orb - d_orb
        achiral_d_orb = d_orb - chiral_d_orb
        chiral_pct = (chiral_d_orb / d_orb) * 100.0 if d_orb > 0 else 0.0

        print(f"Z_{n:<2}   | {subsets:<8,d} | {dn_order:<5d} | {d_orb:<8d} | {c_orb:<8d} | {chiral_d_orb:<13d} | {chiral_pct:<7.1f}%")

        latex_rows.append(
            f"$\\mathbb{{Z}}_{{{n}}}$ & {subsets:,} & {dn_order} & \\textbf{{{d_orb}}} & {c_orb} & {chiral_d_orb} & {chiral_pct:.1f}\\% \\\\"
        )

    if args.latex:
        print("\n% LaTeX Table Rows:")
        for row in latex_rows:
            print(row)

if __name__ == "__main__":
    main()
