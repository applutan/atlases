#!/usr/bin/env python3
"""
generate_poly_atlas_v2.py

Generates the ring-partitioned Inscribed Polygon Atlas for Z_3 through Z_12.

Key improvements:
1. Replaces opaque global master numbering (1..553) with transparent local
   cardinality-based indexing: k-i (e.g. 3-1, 3-2 for triangles), and Forte
   designations for Z_12.
2. Eliminates separate PDF plating pull-ins; generates direct, native LaTeX
   subsections with inline TikZ drawings.
3. Automatically calculates clean page breaks respecting ring and cardinality (k)
   boundaries so no ring starts awkwardly at the bottom of a page.

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import math
import itertools
import csv
import json
from collections import defaultdict

def euler_phi(n):
    return sum(1 for i in range(1, n + 1) if math.gcd(n, i) == 1)

def count_dihedral_bracelets(n, k):
    """Burnside count of subsets of size k under D_n."""
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
        m = (n - 2) // 2
        t1_coeff = 0
        if k % 2 == 0:
            t1_coeff = math.comb(m, k // 2) + (math.comb(m, (k - 2) // 2) if k >= 2 else 0)
        else:
            t1_coeff = 2 * math.comb(m, (k - 1) // 2)

        t2_coeff = math.comb(n // 2, k // 2) if k % 2 == 0 else 0
        refl_sum = (n // 2) * t1_coeff + (n // 2) * t2_coeff

    return (rot_sum + refl_sum) // (2 * n)

def get_d_ops(n):
    """Return all 2n operations (a, b) where x -> (a*x + b) % n."""
    if n == 1:
        return [(1, 0)]
    if n == 2:
        return [(1, 0), (1, 1)]
    return [(a, b) for a in [1, n - 1] for b in range(n)]

def canonicalise_subset(subset, n):
    """Find canonical representative under D_n."""
    if not subset:
        return ()
    d_ops = get_d_ops(n)
    best = None
    for a, b in d_ops:
        cand = tuple(sorted((a * x + b) % n for x in subset))
        if best is None or cand < best:
            best = cand
    return best

def is_subset_achiral(subset, n):
    """Check if subset has bilateral reflection symmetry in D_n."""
    if len(subset) <= 1 or len(subset) >= n - 1:
        return True
    s_set = set(subset)
    for c in range(n):
        refl = {(c - x) % n for x in s_set}
        if refl == s_set:
            return True
    return False

def get_orbit_size(subset, n):
    d_ops = get_d_ops(n)
    seen = set()
    for a, b in d_ops:
        cand = tuple(sorted((a * x + b) % n for x in subset))
        seen.add(cand)
    return len(seen)

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

def generate_all_rings_data(max_n=16):
    all_rings = {}
    for n in range(1, max_n + 1):
        ring_orbits = []
        for k in range(n + 1):
            expected = count_dihedral_bracelets(n, k)
            seen = set()
            k_orbits = []
            for comb in itertools.combinations(range(n), k):
                canon = canonicalise_subset(comb, n)
                if canon not in seen:
                    seen.add(canon)
                    orb_sz = get_orbit_size(canon, n)
                    achiral = is_subset_achiral(canon, n)
                    ivec = compute_interval_vector(canon, n)
                    k_orbits.append({
                        'n': n,
                        'k': k,
                        'subset': canon,
                        'orbit_size': orb_sz,
                        'stab_size': (2 * n) // orb_sz,
                        'is_achiral': achiral,
                        'interval_vector': ivec,
                    })

            # Sort k_orbits: achiral first, then canonical tuple
            k_orbits.sort(key=lambda o: (0 if o['is_achiral'] else 1, o['subset']))
            for idx, o in enumerate(k_orbits, 1):
                o['local_id'] = f"{k}-{idx}"
            assert len(k_orbits) == expected
            ring_orbits.extend(k_orbits)
        all_rings[n] = ring_orbits
    return all_rings

def format_subset_tex(subset):
    if not subset:
        return "\\emptyset"
    return "\\{" + ", ".join(str(x) for x in subset) + "\\}"

def render_mosaic_tikz(o, cx, cy, r=0.62):
    """Emit TikZ code for a single inscribed polygon at (cx, cy)."""
    n = o['n']
    subset = o['subset']
    k = o['k']
    is_achiral = o['is_achiral']
    col_name = "mosaicblue" if is_achiral else "mosaicpink"

    angles = [math.radians(90.0 - v * (360.0 / n)) for v in range(n)]
    cos_v = [math.cos(a) for a in angles]
    sin_v = [math.sin(a) for a in angles]

    lines = []
    # Ambient wireframe
    wire_pts = [f"({cx + r * cos_v[v]:.3f},{cy + r * sin_v[v]:.3f})" for v in range(n)]
    lines.append(f"  \\draw[gray!35, line width=0.25pt] {' -- '.join(wire_pts)} -- cycle;")
    # Ambient vertex tick marks
    for v in range(n):
        lines.append(f"  \\fill[gray!45] ({cx + r * cos_v[v]:.3f},{cy + r * sin_v[v]:.3f}) circle (0.6pt);")

    # Inscribed polygon
    if k == 0:
        lines.append(f"  \\draw[gray!40, line width=0.4pt] ({cx - 0.15:.3f},{cy - 0.15:.3f}) -- ({cx + 0.15:.3f},{cy + 0.15:.3f});")
        lines.append(f"  \\draw[gray!40, line width=0.4pt] ({cx:.3f},{cy:.3f}) circle (0.15cm);")
    elif k == 1:
        v = subset[0]
        vx = cx + r * cos_v[v]
        vy = cy + r * sin_v[v]
        lines.append(f"  \\fill[{col_name}!85!black] ({vx:.3f},{vy:.3f}) circle (2.2pt);")
        lines.append(f"  \\draw[black!85, line width=0.4pt] ({vx:.3f},{vy:.3f}) circle (2.2pt);")
    elif k == 2:
        p1 = f"({cx + r * cos_v[subset[0]]:.3f},{cy + r * sin_v[subset[0]]:.3f})"
        p2 = f"({cx + r * cos_v[subset[1]]:.3f},{cy + r * sin_v[subset[1]]:.3f})"
        lines.append(f"  \\draw[{col_name}, line width=2.4pt, line cap=round] {p1} -- {p2};")
        lines.append(f"  \\draw[black!80, line width=0.4pt, line cap=round] {p1} -- {p2};")
        for v in subset:
            vx = cx + r * cos_v[v]
            vy = cy + r * sin_v[v]
            lines.append(f"  \\fill[{col_name}!85!black] ({vx:.3f},{vy:.3f}) circle (2.0pt);")
    else:
        pts = [f"({cx + r * cos_v[v]:.3f},{cy + r * sin_v[v]:.3f})" for v in subset]
        lines.append(f"  \\fill[{col_name}, fill opacity=0.68] {' -- '.join(pts)} -- cycle;")
        lines.append(f"  \\draw[black!85, line width=0.45pt] {' -- '.join(pts)} -- cycle;")
        for v in subset:
            vx = cx + r * cos_v[v]
            vy = cy + r * sin_v[v]
            lines.append(f"  \\fill[{col_name}!85!black] ({vx:.3f},{vy:.3f}) circle (1.6pt);")

    # NW label: clean local k-i designation
    lines.append(f"  \\node[anchor=north west, font=\\footnotesize\\bfseries\\sffamily, text=black!85, inner sep=0pt] at ({cx - 1.15:.3f},{cy + 0.90:.3f}) {{{o['local_id']}}};")
    # SE label: orbit size
    lines.append(f"  \\node[anchor=south east, font=\\scriptsize\\sffamily, text=black!55, inner sep=0pt] at ({cx + 1.15:.3f},{cy - 0.90:.3f}) {{{o['orbit_size']}}};")

    return "\n".join(lines)

def to_hex(x):
    return f"{x:X}"

def subset_to_slash(s):
    if not s:
        return "//"
    return "/" + "".join(to_hex(x) for x in s) + "/"

def subset_to_comp(s, n):
    if not s:
        return "---"
    if len(s) == 1:
        return to_hex(n)
    m = len(s)
    strides = [(s[(i + 1) % m] - s[i]) % n for i in range(m)]
    return "".join(to_hex(x) for x in strides)

def emit_catalogue_table(all_rings, output_file="polyatlas/gen/poly_catalogue_table.tex"):
    """Emits clean catalogue table using local k-i designations, partition shorthand, and composition sequences."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write("% Auto-generated by generate_poly_atlas_v2.py - Clean Local Catalogue\n")
        f.write("\\begin{longtable}{l l l c c l}\n")
        f.write("\\caption{\\label{tab:poly-full-catalogue}Complete Dihedral Inscribed Polygon Catalogue ($\\mathbb{Z}_3$ to $\\mathbb{Z}_{12}$)}\\\\\n")
        f.write("\\toprule\n")
        f.write("Class & Canonical Subset & Composition & $|\\mathcal{O}|$ & $|\\operatorname{Stab}|$ & Symmetry \\\\\n")
        f.write("\\midrule\n")
        f.write("\\endfirsthead\n")
        f.write("\\caption[]{Complete Dihedral Inscribed Polygon Catalogue (continued)}\\\\\n")
        f.write("\\toprule\n")
        f.write("Class & Canonical Subset & Composition & $|\\mathcal{O}|$ & $|\\operatorname{Stab}|$ & Symmetry \\\\\n")
        f.write("\\midrule\n")
        f.write("\\endhead\n")
        f.write("\\bottomrule\n")
        f.write("\\endfoot\n")

        for n in range(3, 17):
            orbits = all_rings[n]
            f.write(f"\\midrule\n\\multicolumn{{6}}{{l}}{{\\textbf{{Ring $\\mathbb{{Z}}_{{{n}}}$}} ({len(orbits)} orbits)}} \\\\\n\\midrule\n")
            for o in orbits:
                sym_str = "\\textcolor{mosaicblue}{\\textbf{Achiral}}" if o['is_achiral'] else "\\textcolor{mosaicpink}{\\textbf{Chiral}}"
                sub_slash = "\\texttt{" + subset_to_slash(o['subset']) + "}"
                comp_str = "\\texttt{" + subset_to_comp(o['subset'], n) + "}" if o['k'] > 0 else "---"
                f.write(f"\\textbf{{{o['local_id']}}} & {sub_slash} & {comp_str} & {o['orbit_size']} & {o['stab_size']} & {sym_str} \\\\\n")

        f.write("\\bottomrule\n\\end{longtable}\n")
    print(f"✓ Wrote clean catalogue table: {output_file}")

def emit_summary_table(all_rings, output_file="polyatlas/gen/poly_summary_table.tex"):
    """Emits census summary table for Z_1 through Z_16."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write("% Summary Table of Inscribed Polygon Orbits Z_1 to Z_16\n")
        f.write("\\begin{table}[htbp]\n")
        f.write("\\centering\\small\n")
        f.write("\\caption{\\label{tab:poly-census-summary}Dihedral Polygon Orbit Census from $\\mathbb{Z}_1$ to $\\mathbb{Z}_{16}$}\n")
        f.write("\\begin{tabular}{r | r r | r r | r r}\n")
        f.write("\\toprule\n")
        f.write("Ring $\\mathbb{Z}_n$ & $2^n$ Subsets & $|D_n|$ & Dihedral Orbits & Cyclic Orbits & Chiral Pairs & Chiral \\% \\\\\n")
        f.write("\\midrule\n")
        for n in range(1, 17):
            orbits = all_rings[n]
            d_tot = len(orbits)
            chiral_tot = sum(1 for o in orbits if not o['is_achiral'])
            chiral_pairs = chiral_tot
            c_tot = d_tot + chiral_tot
            subsets = 2**n
            dn = 2 * n
            pct = (chiral_tot / d_tot) * 100.0 if d_tot > 0 else 0.0
            f.write(f"$\\mathbb{{Z}}_{{{n}}}$ & {subsets:,} & {dn} & \\textbf{{{d_tot}}} & {c_tot:,} & {chiral_pairs:,} & {pct:.1f}\\% \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")
    print(f"✓ Wrote summary table: {output_file}")

def emit_ring_visual_sections(all_rings, output_file="polyatlas/gen/poly_visual_catalogues.tex"):
    """
    Emits the complete visual catalogue organized ring by ring.
    - Page 1: Z_3, Z_4, Z_5 (4 rows total)
    - Page 2: Z_6, Z_7 (6 rows total, Z_7 completely intact)
    - Page 3: Z_8 (5 rows)
    - Page 4: Z_9 (8 rows, all 46 enneagonals on one single page)
    - Pages 5+: Z_10 through Z_16 with up to 8 rows on first section page, 9 rows on continuation pages.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    ring_names = {
        3: ("The Triangular Ring \\texorpdfstring{$\\mathbb{Z}_3$}{Z3}", 3),
        4: ("The Tetragonal Ring \\texorpdfstring{$\\mathbb{Z}_4$}{Z4}", 4),
        5: ("The Pentagonal Ring \\texorpdfstring{$\\mathbb{Z}_5$}{Z5}", 5),
        6: ("The Hexagonal Ring \\texorpdfstring{$\\mathbb{Z}_6$}{Z6}", 6),
        7: ("The Heptagonal Ring \\texorpdfstring{$\\mathbb{Z}_7$}{Z7}", 7),
        8: ("The Octagonal Ring \\texorpdfstring{$\\mathbb{Z}_8$}{Z8}", 8),
        9: ("The Enneagonal Ring \\texorpdfstring{$\\mathbb{Z}_9$}{Z9}", 9),
        10: ("The Decagonal Ring \\texorpdfstring{$\\mathbb{Z}_{10}$}{Z10}", 10),
        11: ("The Hendecagonal Ring \\texorpdfstring{$\\mathbb{Z}_{11}$}{Z11}", 11),
        12: ("The Dodecagonal Ring \\texorpdfstring{$\\mathbb{Z}_{12}$}{Z12}", 12),
        13: ("The Tridecagonal Ring \\texorpdfstring{$\\mathbb{Z}_{13}$}{Z13}", 13),
        14: ("The Tetradecagonal Ring \\texorpdfstring{$\\mathbb{Z}_{14}$}{Z14}", 14),
        15: ("The Pentadecagonal Ring \\texorpdfstring{$\\mathbb{Z}_{15}$}{Z15}", 15),
        16: ("The Hexadecagonal Ring \\texorpdfstring{$\\mathbb{Z}_{16}$}{Z16}", 16),
    }

    cols = 6
    pitch_x = 2.85
    pitch_y = 2.45

    def write_chunk_tikz(f, chunk):
        f.write("\\noindent\\makebox[\\textwidth][c]{\\begin{tikzpicture}[scale=1.0]\n")
        for idx, o in enumerate(chunk):
            col = idx % cols
            row = idx // cols
            cx = col * pitch_x
            cy = - (row * pitch_y)
            f.write(render_mosaic_tikz(o, cx, cy) + "\n")
        f.write("\\end{tikzpicture}}\\\\[1.0em]\n\n")

    with open(output_file, "w") as f:
        f.write("% Auto-generated by generate_poly_atlas_v2.py - Sectioned Visual Catalogue\n")

        # Group 1: Z_3, Z_4, Z_5 on Page 1
        for n in [3, 4, 5]:
            title, _ = ring_names[n]
            orbits = all_rings[n]
            d_tot = len(orbits)
            chiral_tot = sum(1 for o in orbits if not o['is_achiral'])
            achiral_tot = d_tot - chiral_tot

            f.write(f"\n\\section{{{title}}}\n\\label{{sec:ring-z{n}}}\n\n")
            f.write(f"The cyclic ring $\\mathbb{{Z}}_{{{n}}}$ admits $\\mathbf{{{d_tot}}}$ dihedral orbits ({achiral_tot} \\textcolor{{mosaicblue}}{{\\textbf{{achiral}}}}, {chiral_tot} \\textcolor{{mosaicpink}}{{\\textbf{{chiral}}}}).\\\\\n\n")
            write_chunk_tikz(f, orbits)

        f.write("\n\\clearpage\n")

        # Group 2: Z_6 and Z_7 on Page 2
        for n in [6, 7]:
            title, _ = ring_names[n]
            orbits = all_rings[n]
            d_tot = len(orbits)
            chiral_tot = sum(1 for o in orbits if not o['is_achiral'])
            achiral_tot = d_tot - chiral_tot

            f.write(f"\n\\section{{{title}}}\n\\label{{sec:ring-z{n}}}\n\n")
            f.write(f"The cyclic ring $\\mathbb{{Z}}_{{{n}}}$ admits $\\mathbf{{{d_tot}}}$ dihedral orbits ({achiral_tot} \\textcolor{{mosaicblue}}{{\\textbf{{achiral}}}}, {chiral_tot} \\textcolor{{mosaicpink}}{{\\textbf{{chiral}}}}).\\\\\n\n")
            write_chunk_tikz(f, orbits)

        f.write("\n\\clearpage\n")

        # Rings Z_8 through Z_16: each starts on a fresh page
        for n in range(8, 17):
            title, _ = ring_names[n]
            orbits = all_rings[n]
            d_tot = len(orbits)
            chiral_tot = sum(1 for o in orbits if not o['is_achiral'])
            achiral_tot = d_tot - chiral_tot

            # First page of ring n has section header: capacity is 8 rows (48 orbits)
            first_page_cap = 8 * cols
            cont_page_cap = 9 * cols

            first_chunk = orbits[:first_page_cap]
            rem_orbits = orbits[first_page_cap:]

            f.write(f"\n\\section{{{title}}}\n\\label{{sec:ring-z{n}}}\n\n")
            f.write(f"The cyclic ring $\\mathbb{{Z}}_{{{n}}}$ admits $\\mathbf{{{d_tot}}}$ dihedral orbits ({achiral_tot} \\textcolor{{mosaicblue}}{{\\textbf{{achiral}}}}, {chiral_tot} \\textcolor{{mosaicpink}}{{\\textbf{{chiral}}}}).\\\\\n\n")
            write_chunk_tikz(f, first_chunk)

            # Continuation pages
            while rem_orbits:
                chunk = rem_orbits[:cont_page_cap]
                rem_orbits = rem_orbits[cont_page_cap:]
                f.write("\n\\clearpage\n\\noindent\\textbf{\\textsf{" + f"{title} (continued)" + "}}\\\\[0.5em]\n\n")
                write_chunk_tikz(f, chunk)

            if n < 16:
                f.write("\n\\clearpage\n")

    print(f"✓ Wrote sectioned visual catalogue: {output_file}")

def emit_greppable_dataset(all_rings, data_dir="polyatlas/data"):
    """Emits clean, streamlined TSV, CSV, and JSON datasets for computational querying."""
    os.makedirs(data_dir, exist_ok=True)
    tsv_path = os.path.join(data_dir, "inngons.tsv")
    csv_path = os.path.join(data_dir, "inngons.csv")
    json_path = os.path.join(data_dir, "inngons.json")

    rows = []
    for n in range(1, 17):
        for o in all_rings[n]:
            k = o['k']
            subset = o['subset']
            comp = subset_to_comp(subset, n) if k > 0 else "---"
            slash = subset_to_slash(subset)
            row = {
                "composition": comp,
                "class_id": o['local_id'],
                "n": n,
                "k": k,
                "subset": slash,
                "orbit_size": o['orbit_size'],
                "is_achiral": 1 if o['is_achiral'] else 0
            }
            rows.append(row)

    headers = [
        "composition", "class_id", "n", "k", "subset", "orbit_size", "is_achiral"
    ]

    # Write TSV
    with open(tsv_path, "w", encoding="utf-8") as f:
        f.write("# Inscribed Polygons Dihedral Orbit Census (Z_1 to Z_16)\n")
        f.write("# Fields: " + ", ".join(headers) + "\n")
        f.write("\t".join(headers) + "\n")
        for r in rows:
            f.write("\t".join(str(r[h]) for h in headers) + "\n")

    # Write CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    # Write JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print(f"✓ Wrote streamlined TSV dataset: {tsv_path}")
    print(f"✓ Wrote streamlined CSV dataset: {csv_path}")
    print(f"✓ Wrote streamlined JSON dataset: {json_path}")

def main():
    print("=" * 80)
    print("GENERATING SECTIONED VISUAL ATLAS FOR Z_3 TO Z_16")
    print("=" * 80)
    all_rings = generate_all_rings_data(16)
    emit_summary_table(all_rings)
    emit_catalogue_table(all_rings)
    emit_ring_visual_sections(all_rings)
    emit_greppable_dataset(all_rings)

if __name__ == "__main__":
    main()
