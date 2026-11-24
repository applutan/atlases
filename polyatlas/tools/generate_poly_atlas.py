#!/usr/bin/env python3
"""
generate_poly_atlas.py

Generates the complete census and visual atlas of single inscribed polygons
(binary bracelets / subsets under D_n) for cyclic rings Z_3 through Z_12.

Computes:
1. All 553 non-equivalent dihedral orbits across Z_3 to Z_12.
2. Bilateral symmetry (achiral: Mosaic Blue vs chiral: Mosaic Pink).
3. Canonical representatives (lexicographical prime form).
4. Analytical LaTeX tables (summary census and complete 553-entry index).
5. Standalone TikZ visual plates PDF displaying all 553 inscribed polygons.

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import math
import itertools
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
    return [(a, b) for a in [1, n - 1] for b in range(n)]

def canonicalise_subset(subset, n):
    """
    Find canonical representative of a subset under D_n.
    Returns sorted tuple of vertices.
    """
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
        # reflection x -> (c - x) % n
        refl = {(c - x) % n for x in s_set}
        if refl == s_set:
            return True
    return False

def get_orbit_size(subset, n):
    """Compute size of D_n orbit of subset."""
    d_ops = get_d_ops(n)
    seen = set()
    for a, b in d_ops:
        cand = tuple(sorted((a * x + b) % n for x in subset))
        seen.add(cand)
    return len(seen)

def compute_interval_vector(subset, n):
    """Compute circular distance multiset (interval vector)."""
    m = len(subset)
    if m <= 1:
        return ()
    dist_counts = defaultdict(int)
    for i in range(m):
        for j in range(i + 1, m):
            d = min((subset[j] - subset[i]) % n, (subset[i] - subset[j]) % n)
            dist_counts[d] += 1
    return tuple(dist_counts[d] for d in range(1, n // 2 + 1))

def generate_all_orbits(max_n=12):
    """Compute all D_n orbits for n from 3 to max_n."""
    all_rings_data = {}
    grand_total = 0

    for n in range(3, max_n + 1):
        ring_orbits = []
        d_ops = get_d_ops(n)

        for k in range(n + 1):
            expected_count = count_dihedral_bracelets(n, k)
            seen_orbits = set()
            k_orbits = []

            for comb in itertools.combinations(range(n), k):
                canon = canonicalise_subset(comb, n)
                if canon not in seen_orbits:
                    seen_orbits.add(canon)
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

            # Sort k_orbits: achiral first, then by canonical tuple
            k_orbits.sort(key=lambda o: (0 if o['is_achiral'] else 1, o['subset']))
            for idx, o in enumerate(k_orbits, 1):
                o['local_id'] = f"{k}-{idx}"

            assert len(k_orbits) == expected_count, f"Mismatch in Z_{n} for k={k}: got {len(k_orbits)}, expected {expected_count}"
            ring_orbits.extend(k_orbits)

        for idx, o in enumerate(ring_orbits, 1):
            o['ring_global_id'] = idx
            grand_total += 1
            o['master_id'] = grand_total

        all_rings_data[n] = ring_orbits
        print(f"Ring Z_{n:2d}: {len(ring_orbits):3d} orbits (Total verified)")

    print(f"Grand Total Orbits across Z_3..Z_{max_n}: {grand_total}")
    return all_rings_data

def format_subset_str(subset):
    if not subset:
        return "\\emptyset"
    return "\\{" + ", ".join(str(x) for x in subset) + "\\}"

def emit_latex_tables(all_rings_data, output_dir="polyatlas/gen"):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Summary Table across Z_3 to Z_12
    summary_path = os.path.join(output_dir, "poly_summary_table.tex")
    with open(summary_path, "w") as f:
        f.write("% Summary Table of Inscribed Polygon Orbits Z_3 to Z_12\n")
        f.write("\\begin{table}[htbp]\n\\centering\\small\n")
        f.write("\\caption{\\label{tab:poly-census-summary}Dihedral Polygon Orbit Census from $\\mathbb{Z}_3$ to $\\mathbb{Z}_{12}$}\n")
        f.write("\\begin{tabular}{r | r r | r r | r r}\n")
        f.write("\\toprule\n")
        f.write("Ring $\\mathbb{Z}_n$ & $2^n$ Subsets & $|D_n|$ & Dihedral Orbits & Cyclic Orbits & Chiral Pairs & Chiral \\% \\\\\n")
        f.write("\\midrule\n")

        cum_d = 0
        for n, orbits in all_rings_data.items():
            d_tot = len(orbits)
            cum_d += d_tot
            chiral_d = sum(1 for o in orbits if not o['is_achiral'])
            c_tot = d_tot + chiral_d
            pct = (chiral_d / d_tot * 100) if d_tot > 0 else 0
            f.write(f"$\\mathbb{{Z}}_{{{n}}}$ & {2**n:,} & {2*n} & \\textbf{{{d_tot}}} & {c_tot} & {chiral_d} & {pct:.1f}\\% \\\\\n")

        f.write("\\midrule\\midrule\n")
        f.write(f"\\textbf{{Grand Total}} & --- & --- & \\textbf{{{cum_d}}} & --- & --- & --- \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
    print(f"✓ Wrote summary table: {summary_path}")

    # 2. Detailed 553-entry Catalogue
    cat_path = os.path.join(output_dir, "poly_catalogue_table.tex")
    with open(cat_path, "w") as f:
        f.write("% Full 553-Entry Dihedral Polygon Catalogue\n")
        f.write("\\begin{longtable}{r l l c c l}\n")
        f.write("\\caption{\\label{tab:poly-full-catalogue}Complete Dihedral Inscribed Polygon Catalogue ($\\mathbb{Z}_3$ to $\\mathbb{Z}_{12}$, $553$ Orbits)}\\\\\n")
        f.write("\\toprule\n")
        f.write("ID & Class & Canonical Subset & $|\\mathcal{O}|$ & $|\\operatorname{Stab}|$ & Symmetry \\\\\n")
        f.write("\\midrule\n")
        f.write("\\endfirsthead\n")
        f.write("\\caption[]{Complete Dihedral Inscribed Polygon Catalogue (continued)}\\\\\n")
        f.write("\\toprule\n")
        f.write("ID & Class & Canonical Subset & $|\\mathcal{O}|$ & $|\\operatorname{Stab}|$ & Symmetry \\\\\n")
        f.write("\\midrule\n")
        f.write("\\endhead\n")
        f.write("\\bottomrule\n")
        f.write("\\endfoot\n")

        for n, orbits in all_rings_data.items():
            f.write(f"\\midrule\n\\multicolumn{{6}}{{l}}{{\\textbf{{Ring $\\mathbb{{Z}}_{{{n}}}$}} ({len(orbits)} orbits)}} \\\\\n\\midrule\n")
            curr_k = None
            for o in orbits:
                sym_str = "\\textcolor{mosaicblue}{\\textbf{Achiral}}" if o['is_achiral'] else "\\textcolor{mosaicpink}{\\textbf{Chiral}}"
                sub_str = format_subset_str(o['subset'])
                f.write(f"\\textbf{{{o['master_id']}}} & $\\mathbb{{Z}}_{{{n}}}\\text{{-}}{o['local_id']}$ & ${sub_str}$ & {o['orbit_size']} & {o['stab_size']} & {sym_str} \\\\\n")

        f.write("\\bottomrule\n\\end{longtable}\n")
    print(f"✓ Wrote full catalogue table: {cat_path}")

def emit_tikz_plates(all_rings_data, output_dir="polyatlas/plates"):
    os.makedirs(output_dir, exist_ok=True)
    plate_tex_path = os.path.join(output_dir, "poly_plates.tex")

    # Grid layout: 6 columns x 10 rows per page
    # r = 0.62 cm, pitch_x = 2.90 cm, pitch_y = 2.45 cm
    cols = 6
    pitch_x = 2.90
    pitch_y = 2.45
    r = 0.62

    # Group into pages cleanly by rings:
    # Page 1: Z_3, Z_4, Z_5, Z_6 (4 + 6 + 8 + 13 = 31 drawings)
    # Page 2: Z_7 (18) + Z_8 (30) = 48 drawings
    # Page 3: Z_9 (46 drawings)
    # Page 4: Z_10 part 1 (k=0..5, 42 drawings)
    # Page 5: Z_10 part 2 (k=6..10, 36 drawings)
    # Page 6: Z_11 part 1 (k=0..5, 63 drawings)
    # Page 7: Z_11 part 2 (k=6..11, 63 drawings)
    # Page 8: Z_12 part 1 (k=0..4, 49 drawings)
    # Page 9: Z_12 part 2 (k=5, 38 drawings)
    # Page 10: Z_12 part 3 (k=6, 50 drawings)
    # Page 11: Z_12 part 4 (k=7..12, 87 drawings -> split or 2 pages?)
    # Let's make an automated page packager that respects ring and k boundaries!

    flat_list = []
    for n, orbits in all_rings_data.items():
        flat_list.extend(orbits)

    # 553 items. If per page = 54 (6 cols x 9 rows), that's ~10 pages.
    # Let's allow max 54 items per page to leave room for ring title banner!
    max_per_page = 54

    pages = []
    curr_page = []

    # Pack by ring where possible
    for n in range(3, 13):
        ring_items = all_rings_data[n]
        if len(curr_page) + len(ring_items) <= max_per_page:
            curr_page.extend(ring_items)
        else:
            if curr_page:
                pages.append(curr_page)
                curr_page = []
            # If ring fits in one page:
            if len(ring_items) <= max_per_page:
                curr_page.extend(ring_items)
            else:
                # Ring is larger than max_per_page (e.g. Z_10=78, Z_11=126, Z_12=224)
                # Split ring by k
                k_dict = defaultdict(list)
                for item in ring_items:
                    k_dict[item['k']].append(item)
                for k in range(n + 1):
                    k_items = k_dict[k]
                    if len(curr_page) + len(k_items) <= max_per_page:
                        curr_page.extend(k_items)
                    else:
                        if curr_page:
                            pages.append(curr_page)
                            curr_page = []
                        curr_page.extend(k_items)

    if curr_page:
        pages.append(curr_page)

    print(f"Total Plate Pages generated: {len(pages)}")

    with open(plate_tex_path, "w") as f:
        f.write("% Auto-generated by generate_poly_atlas.py - Visual Plates for Inscribed Polygons\n")
        f.write("\\documentclass[11pt,a4paper]{article}\n")
        f.write("\\usepackage[margin=1.2cm]{geometry}\n")
        f.write("\\usepackage{amsmath,amssymb}\n")
        f.write("\\usepackage{tikz}\n")
        f.write("\\usepackage{xcolor}\n")
        f.write("\\definecolor{mosaicblue}{RGB}{74, 128, 196}\n")
        f.write("\\definecolor{mosaicpink}{RGB}{224, 102, 102}\n")
        f.write("\\pagestyle{empty}\n")
        f.write("\\begin{document}\n\n")

        for page_idx, page_items in enumerate(pages, 1):
            f.write(f"% Plate Page {page_idx} ({len(page_items)} mosaics)\n")
            f.write("\\noindent\\makebox[\\textwidth][c]{\\begin{tikzpicture}[scale=1.0]\n")

            for idx_in_page, o in enumerate(page_items):
                col = idx_in_page % cols
                row = idx_in_page // cols
                cx = col * pitch_x
                cy = - (row * pitch_y)
                n = o['n']
                subset = o['subset']
                k = o['k']
                is_achiral = o['is_achiral']
                col_name = "mosaicblue" if is_achiral else "mosaicpink"

                # Precompute vertex positions for ambient n-gon: 0 at top, clockwise
                angles = [math.radians(90.0 - v * (360.0 / n)) for v in range(n)]
                cos_v = [math.cos(a) for a in angles]
                sin_v = [math.sin(a) for a in angles]

                # Ambient n-gon wireframe
                wire_pts = [f"({cx + r * cos_v[v]:.3f},{cy + r * sin_v[v]:.3f})" for v in range(n)]
                f.write(f"  \\draw[gray!35, line width=0.25pt] {' -- '.join(wire_pts)} -- cycle;\n")

                # Ambient vertex tick pips (light dots)
                for v in range(n):
                    f.write(f"  \\fill[gray!45] ({cx + r * cos_v[v]:.3f},{cy + r * sin_v[v]:.3f}) circle (0.6pt);\n")

                # Draw inscribed polygon
                if k == 0:
                    # Empty set: central subtle null marker
                    f.write(f"  \\draw[gray!40, line width=0.4pt] ({cx - 0.15:.3f},{cy - 0.15:.3f}) -- ({cx + 0.15:.3f},{cy + 0.15:.3f});\n")
                    f.write(f"  \\draw[gray!40, line width=0.4pt] ({cx:.3f},{cy:.3f}) circle (0.15cm);\n")
                elif k == 1:
                    # Unigon: prominent vertex node
                    v = subset[0]
                    vx = cx + r * cos_v[v]
                    vy = cy + r * sin_v[v]
                    f.write(f"  \\fill[{col_name}!85!black] ({vx:.3f},{vy:.3f}) circle (2.2pt);\n")
                    f.write(f"  \\draw[black!85, line width=0.4pt] ({vx:.3f},{vy:.3f}) circle (2.2pt);\n")
                elif k == 2:
                    # Digon: thick chord between two vertices
                    p1 = f"({cx + r * cos_v[subset[0]]:.3f},{cy + r * sin_v[subset[0]]:.3f})"
                    p2 = f"({cx + r * cos_v[subset[1]]:.3f},{cy + r * sin_v[subset[1]]:.3f})"
                    f.write(f"  \\draw[{col_name}, line width=2.4pt, line cap=round] {p1} -- {p2};\n")
                    f.write(f"  \\draw[black!80, line width=0.4pt, line cap=round] {p1} -- {p2};\n")
                    for v in subset:
                        vx = cx + r * cos_v[v]
                        vy = cy + r * sin_v[v]
                        f.write(f"  \\fill[{col_name}!85!black] ({vx:.3f},{vy:.3f}) circle (2.0pt);\n")
                else:
                    # k-gon: shaded polygon with boundary chords and vertex nodes
                    pts = [f"({cx + r * cos_v[v]:.3f},{cy + r * sin_v[v]:.3f})" for v in subset]
                    f.write(f"  \\fill[{col_name}, fill opacity=0.68] {' -- '.join(pts)} -- cycle;\n")
                    f.write(f"  \\draw[black!85, line width=0.45pt] {' -- '.join(pts)} -- cycle;\n")
                    for v in subset:
                        vx = cx + r * cos_v[v]
                        vy = cy + r * sin_v[v]
                        f.write(f"  \\fill[{col_name}!85!black] ({vx:.3f},{vy:.3f}) circle (1.6pt);\n")

                # NW corner: Master ID and Class
                label_text = f"\\textbf{{{o['master_id']}}}"
                f.write(f"  \\node[anchor=north west, font=\\footnotesize\\sffamily, text=black!85, inner sep=0pt] at ({cx - 1.20:.3f},{cy + 0.90:.3f}) {{{label_text}}};\n")
                # NW sub-label: ring & class e.g. "Z8: 3-2"
                class_text = f"$\\mathbb{{Z}}_{{{n}}}\\text{{-}}{o['local_id']}$"
                f.write(f"  \\node[anchor=north west, font=\\tiny\\sffamily, text=black!55, inner sep=0pt] at ({cx - 1.20:.3f},{cy + 0.65:.3f}) {{{class_text}}};\n")
                # SE corner: Orbit size |O|
                f.write(f"  \\node[anchor=south east, font=\\scriptsize\\sffamily, text=black!55, inner sep=0pt] at ({cx + 1.20:.3f},{cy - 0.90:.3f}) {{{o['orbit_size']}}};\n")

            f.write("\\end{tikzpicture}}\\clearpage\n\n")

        f.write("\\end{document}\n")
    print(f"✓ Wrote visual plates TikZ source: {plate_tex_path}")

def main():
    print("=" * 80)
    print("POLYATLAS GENERATOR: INSCRIBED POLYGON CENSUS FROM Z_3 TO Z_12")
    print("=" * 80)
    all_rings_data = generate_all_orbits(max_n=12)
    emit_latex_tables(all_rings_data)
    emit_tikz_plates(all_rings_data)

if __name__ == "__main__":
    main()
