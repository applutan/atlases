#!/usr/bin/env python3
"""
compute_orbit_polynomials.py - Generate Cyclic and Dihedral Orbit Polynomials

Computes the exact cyclic necklace polynomial N_n(x) and dihedral Cauchy-Frobenius
bracelet polynomial CF_n(x) for circular rings Z_1 through Z_n using the cycle index
under the binary configuration substitution z_k -> 1 + x^k.

Mathematical Formulations:
  Cyclic (Necklaces):
    N_n(x) = (1/n) * sum_{d|n} phi(d) * (1 + x^d)^(n/d)

  Dihedral (Bracelets, Cauchy-Frobenius):
    n odd:
      CF_n(x) = (1/2) * N_n(x) + (1/2) * (1 + x) * (1 + x^2)^((n-1)/2)
    n even:
      CF_n(x) = (1/2) * N_n(x) + (1/4) * (1 + x)^2 * (1 + x^2)^((n-2)/2) + (1/4) * (1 + x^2)^(n/2)

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import math
import argparse
from typing import List, Tuple, Dict


def euler_phi(n: int) -> int:
    """Compute Euler's totient function phi(n)."""
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


def poly_add(p1: List[int], p2: List[int]) -> List[int]:
    """Add two polynomials represented as coefficient lists."""
    deg = max(len(p1), len(p2))
    res = [0] * deg
    for i in range(deg):
        c1 = p1[i] if i < len(p1) else 0
        c2 = p2[i] if i < len(p2) else 0
        res[i] = c1 + c2
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


def poly_scale(p: List[int], s: int) -> List[int]:
    """Scale a polynomial by an integer scalar s."""
    return [c * s for c in p]


def poly_mul(p1: List[int], p2: List[int]) -> List[int]:
    """Multiply two polynomials."""
    deg = len(p1) + len(p2) - 1
    res = [0] * deg
    for i, c1 in enumerate(p1):
        for j, c2 in enumerate(p2):
            res[i + j] += c1 * c2
    return res


def poly_pow(p: List[int], exp: int) -> List[int]:
    """Raise polynomial p to non-negative power exp."""
    res = [1]
    base = list(p)
    e = exp
    while e > 0:
        if e % 2 == 1:
            res = poly_mul(res, base)
        base = poly_mul(base, base)
        e //= 2
    return res


def compute_cyclic_polynomial(n: int) -> List[int]:
    """Compute N_n(x) = (1/n) * sum_{d|n} phi(d) * (1 + x^d)^(n/d)."""
    accum = [0]
    for d in range(1, n + 1):
        if n % d == 0:
            phi_d = euler_phi(d)
            # Factor: (1 + x^d)
            factor = [0] * (d + 1)
            factor[0] = 1
            factor[d] = 1
            power = n // d
            term = poly_pow(factor, power)
            term_scaled = poly_scale(term, phi_d)
            accum = poly_add(accum, term_scaled)
    # Divide every coefficient by n
    res = []
    for c in accum:
        assert c % n == 0, f"Coefficient {c} not divisible by {n}"
        res.append(c // n)
    return res


def compute_dihedral_polynomial(n: int, cyclic_poly: List[int]) -> List[int]:
    """
    Compute CF_n(x) (Cauchy-Frobenius / Burnside bracelet polynomial).
    """
    cyclic_scaled = poly_scale(cyclic_poly, n)  # n * N_n(x)
    reflections = [0]

    # Factor (1 + x^2)
    one_plus_x2 = [1, 0, 1]
    one_plus_x = [1, 1]

    if n % 2 == 1:
        # Odd n: n reflections, each fixes 1 vertex and (n-1)/2 chords:
        # reflection term = n * (1 + x) * (1 + x^2)^((n-1)/2)
        power = (n - 1) // 2
        ref = poly_pow(one_plus_x2, power)
        ref = poly_mul(one_plus_x, ref)
        reflections = poly_scale(ref, n)
    else:
        # Even n: n/2 vertex-vertex reflections and n/2 edge-edge reflections
        # term1 = (n/2) * (1 + x)^2 * (1 + x^2)^((n-2)/2)
        p1 = (n - 2) // 2
        ref1 = poly_pow(one_plus_x2, p1)
        ref1 = poly_mul(poly_pow(one_plus_x, 2), ref1)
        ref1_scaled = poly_scale(ref1, n // 2)

        # term2 = (n/2) * (1 + x^2)^(n/2)
        p2 = n // 2
        ref2 = poly_pow(one_plus_x2, p2)
        ref2_scaled = poly_scale(ref2, n // 2)

        reflections = poly_add(ref1_scaled, ref2_scaled)

    # Total dihedral = (1/(2n)) * (cyclic_scaled + reflections)
    total_accum = poly_add(cyclic_scaled, reflections)
    res = []
    for c in total_accum:
        assert c % (2 * n) == 0, f"Coefficient {c} not divisible by 2n={2*n}"
        res.append(c // (2 * n))
    return res


def format_polynomial(poly: List[int], var: str = "x") -> str:
    """Format polynomial coefficients into conventional LaTeX/string notation."""
    terms = []
    for deg, c in enumerate(poly):
        if c == 0:
            continue
        if deg == 0:
            terms.append(f"{c}")
        elif deg == 1:
            terms.append(f"{c}{var}" if c != 1 else f"{var}")
        else:
            terms.append(f"{c}{var}^{deg}" if c != 1 else f"{var}^{deg}")
    return " + ".join(terms) if terms else "0"


def format_polynomial_latex_split(poly: List[int], var: str = "x", max_terms_per_line: int = 6) -> str:
    """Format polynomial into multiline LaTeX string."""
    terms = []
    for deg, c in enumerate(poly):
        if c == 0:
            continue
        if deg == 0:
            terms.append(f"{c}")
        elif deg == 1:
            terms.append(f"{c}{var}" if c != 1 else f"{var}")
        else:
            terms.append(f"{c}{var}^{{{deg}}}" if c != 1 else f"{var}^{{{deg}}}")

    lines = []
    curr = []
    for t in terms:
        curr.append(t)
        if len(curr) >= max_terms_per_line:
            lines.append(" + ".join(curr))
            curr = []
    if curr:
        lines.append(" + ".join(curr))
    return " + \\\\\n  &\\quad + ".join(lines)


def generate_coefficient_table_latex(results: List[Dict], mode: str = "dihedral", max_n: int = 16) -> str:
    """Generate clean 19-column LaTeX coefficient table."""
    lines = []
    if mode == "dihedral":
        cap = "\\label{tab:dihedral-coefficients}Dihedral Inscribed Polygon Census Coefficients $c_{n,k}$ ($CF_n(x)$ Orbit Counts under $D_n$)"
        poly_sym = "c_{n,k}"
    elif mode == "cyclic":
        cap = "\\label{tab:cyclic-coefficients}Cyclic Inscribed Polygon Census Coefficients $a_{n,k}$ ($N_n(x)$ Orbit Counts under $C_n$)"
        poly_sym = "a_{n,k}"
    else:
        cap = "\\label{tab:chiral-coefficients}Chiral Enantiomorphic Pairs $\\chi_{n,k} = a_{n,k} - c_{n,k}$ from $\\mathbb{Z}_1$ to $\\mathbb{Z}_{16}$"
        poly_sym = "\\chi_{n,k}"

    lines.append("% Auto-generated by compute_orbit_polynomials.py")
    lines.append("\\begin{table}[htbp]")
    lines.append("\\centering\\footnotesize")
    lines.append("\\setlength{\\tabcolsep}{2.5pt}")
    lines.append(f"\\caption{{{cap}}}")
    lines.append("\\begin{tabular}{r | rrrrrrrrrrrrrrrrr | r}")
    lines.append("\\toprule")
    cols_header = " & ".join(["$n$"] + [f"${k}$" for k in range(max_n + 1)] + ["$\\Sigma$"])
    lines.append(f"{cols_header} \\\\")
    lines.append("\\midrule")

    for r in results:
        n = r["n"]
        if mode == "dihedral":
            coeffs = r["dihedral"]
            tot = r["dihedral_sum"]
        elif mode == "cyclic":
            coeffs = r["cyclic"]
            tot = r["cyclic_sum"]
        else:
            coeffs = [r["cyclic"][i] - r["dihedral"][i] for i in range(len(r["cyclic"]))]
            tot = r["chiral_pairs"]

        row = [f"$\\mathbb{{Z}}_{{{n}}}$"]
        for k in range(max_n + 1):
            if k < len(coeffs):
                val = coeffs[k]
                row.append(f"{val}" if val > 0 or k <= n else "--")
            else:
                row.append("--")
        row.append(f"\\textbf{{{tot}}}")
        lines.append(" & ".join(row) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compute exact Cyclic N_n(x) and Dihedral Cauchy-Frobenius CF_n(x) polynomials."
    )
    parser.add_argument("-n", "--max-n", type=int, default=16, help="Maximum n (default: 16)")
    parser.add_argument("--format", choices=["text", "latex", "tables", "all"], default="all", help="Output format")
    parser.add_argument("-o", "--output", default=None, help="Optional output LaTeX file")
    parser.add_argument("--gen-dir", default=None, help="Optional gen directory to save coefficient tables")
    args = parser.parse_args()

    results = []
    for n in range(1, args.max_n + 1):
        cyc = compute_cyclic_polynomial(n)
        dih = compute_dihedral_polynomial(n, cyc)
        cyc_sum = sum(cyc)
        dih_sum = sum(dih)
        results.append({
            "n": n,
            "cyclic": cyc,
            "dihedral": dih,
            "cyclic_sum": cyc_sum,
            "dihedral_sum": dih_sum,
            "chiral_pairs": cyc_sum - dih_sum
        })

    if args.format in ["text", "all"]:
        print("=" * 80)
        print(f"  CYCLIC N_n(x) & CAUCHY-FROBENIUS CF_n(x) POLYNOMIALS (n = 1 .. {args.max_n})")
        print("=" * 80)
        for r in results:
            n = r["n"]
            print(f"\n--- Ring Z_{n} (D_{n} order {2*n}, C_{n} order {n}) ---")
            print(f"  N_{n}(x)   = {format_polynomial(r['cyclic'])}")
            print(f"             [N_{n}(1) = {r['cyclic_sum']} cyclic orbits]")
            print(f"  CF_{n}(x)  = {format_polynomial(r['dihedral'])}")
            print(f"             [CF_{n}(1) = {r['dihedral_sum']} dihedral orbits; {r['chiral_pairs']} chiral pairs]")

    if args.format in ["tables", "all"] or args.gen_dir:
        dih_table = generate_coefficient_table_latex(results, mode="dihedral", max_n=args.max_n)
        cyc_table = generate_coefficient_table_latex(results, mode="cyclic", max_n=args.max_n)
        chi_table = generate_coefficient_table_latex(results, mode="chiral", max_n=args.max_n)

        combined_tables = f"{dih_table}\n\n\\bigskip\n\n{cyc_table}\n\n\\bigskip\n\n{chi_table}\n"

        if args.gen_dir:
            import os
            out_path = os.path.join(args.gen_dir, "poly_coefficient_tables.tex")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(combined_tables)
            print(f"\n✓ Generated coefficient tables in: {out_path}")

    if args.format in ["latex", "all"] and args.output:
        latex_lines = []
        latex_lines.append("% Auto-generated by compute_orbit_polynomials.py")
        latex_lines.append("\\begin{longtable}{r l}")
        latex_lines.append("\\toprule")
        latex_lines.append("Ring $\\mathbb{Z}_n$ & Generating Polynomials ($CF_n(x)$ Dihedral, $N_n(x)$ Cyclic) \\\\")
        latex_lines.append("\\midrule")
        latex_lines.append("\\endfirsthead")
        latex_lines.append("\\toprule")
        latex_lines.append("Ring $\\mathbb{Z}_n$ & Generating Polynomials ($CF_n(x)$ Dihedral, $N_n(x)$ Cyclic) \\\\")
        latex_lines.append("\\midrule")
        latex_lines.append("\\endhead")
        latex_lines.append("\\bottomrule")
        latex_lines.append("\\endfoot")

        for r in results:
            n = r["n"]
            dih_fmt = format_polynomial(r["dihedral"])
            cyc_fmt = format_polynomial(r["cyclic"])
            is_same = (r["dihedral"] == r["cyclic"])

            latex_lines.append(f"\\multirow{{2}}{{*}}{{\\textbf{{$\\mathbb{{Z}}_{{{n}}}$}}}} & ")
            latex_lines.append(f"  $CF_{{{n}}}(x) = {dih_fmt}$ \\hfill ($\\Sigma = {r['dihedral_sum']}$) \\\\")
            if is_same:
                latex_lines.append(f"  & \\quad\\footnotesize(Achiral lattice: $N_{{{n}}}(x) \\equiv CF_{{{n}}}(x)$, 0 chiral pairs) \\\\[0.6em]")
            else:
                latex_lines.append(f"  & $N_{{{n}}}(x) = {cyc_fmt}$ \\hfill ($\\Sigma = {r['cyclic_sum']}$, {r['chiral_pairs']} chiral pairs) \\\\[0.6em]")

        latex_lines.append("\\end{longtable}")
        latex_str = "\n".join(latex_lines)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(latex_str)
        print(f"\n✓ Wrote LaTeX list to {args.output}")

if __name__ == "__main__":
    main()
