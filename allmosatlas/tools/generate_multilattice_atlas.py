#!/usr/bin/env python3
"""
generate_multilattice_atlas.py - Complete Dihedral Orbit Generator and Plate Builder for Z_1..Z_8

Generates the complete census of dihedral composition mosaics (set partitions of Z_n
under the physical dihedral group D_n) for rings Z_1 through Z_8 (509 total mosaics
across 5,295 set partitions).

Outputs:
1. LaTeX summary census tables (consolidated orbit statistics, orbit polynomials).
2. TikZ visual plates (10 pages) displaying all 509 pure shaded mosaics.
3. Master analytical datasets linking all mosaics and constituent blocks.

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import math
import argparse
from collections import defaultdict
from typing import List, Tuple, Dict, Any, Set

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate complete dihedral composition mosaic atlas and plates for Z_1 through Z_8."
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=8,
        help="Maximum cyclic ring order (default: 8)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="allmosatlas",
        help="Base output directory for allmosatlas"
    )
    return parser.parse_args()

def get_dihedral_ops(n: int) -> List[Tuple[int, int]]:
    """Return all elements of D_n as (a, b) representing x -> (a*x + b) % n."""
    if n == 1:
        return [(1, 0)]
    if n == 2:
        return [(1, 0), (1, 1)]  # D_2 order 2
    ops = []
    for a in [1, -1]:
        for b in range(n):
            ops.append((a, b % n))
    return ops

def get_partitions(elements: List[int]) -> List[List[List[int]]]:
    """Generate all set partitions of a given list of elements."""
    if not elements:
        return [[]]
    first = elements[0]
    rest = elements[1:]
    sub_partitions = get_partitions(rest)
    result = []
    for sp in sub_partitions:
        # Option 1: first is its own block
        result.append([[first]] + sp)
        # Option 2: first joins an existing block
        for i in range(len(sp)):
            new_sp = [list(b) for b in sp]
            new_sp[i] = [first] + new_sp[i]
            result.append(new_sp)
    return result

def is_block_symmetric(block: List[int], n: int) -> bool:
    """Check if a block is invariant under some reflection in D_n."""
    if n == 1 or len(block) <= 2:
        return True
    b_set = set(block)
    # Check all n reflections: x -> (b - x) % n
    for b in range(n):
        refl = {(b - x) % n for x in b_set}
        if refl == b_set:
            return True
    return False

def compute_block_energy(block: List[int], n: int) -> int:
    """Compute sum of squared circular chord distances."""
    if n <= 1:
        return 0
    e = 0
    m = len(block)
    for i in range(m):
        for j in range(i + 1, m):
            d = min((block[j] - block[i]) % n, (block[i] - block[j]) % n)
            e += d * d
    return e

def canonicalise_partition(part: List[List[int]], n: int) -> List[List[int]]:
    """Find canonical representative under D_n."""
    ops = get_dihedral_ops(n)
    best = None
    for a, b in ops:
        cand = [sorted((a * x + b) % n for x in blk) for blk in part]
        cand.sort(key=lambda blk: (min(blk), blk))
        cand_tuple = tuple(tuple(blk) for blk in cand)
        if best is None or cand_tuple < best:
            best = cand_tuple
    return [list(blk) for blk in best]

def get_orbit(part: List[List[int]], n: int) -> Set[Tuple[Tuple[int, ...], ...]]:
    """Get all distinct partitions in the D_n orbit."""
    ops = get_dihedral_ops(n)
    orb = set()
    for a, b in ops:
        cand = [sorted((a * x + b) % n for x in blk) for blk in part]
        cand.sort(key=lambda blk: (min(blk), blk))
        cand_tuple = tuple(tuple(blk) for blk in cand)
        orb.add(cand_tuple)
    return orb

def format_slash(part: List[List[int]]) -> str:
    """Format partition in hexadecimal slash notation."""
    blocks_str = []
    for blk in part:
        s = "".join(f"{x:X}" for x in sorted(blk))
        blocks_str.append(s)
    return "/" + "/".join(blocks_str) + "/"

def compute_ring_mosaics(n: int) -> Dict[str, Any]:
    """Compute complete dihedral mosaic census for ring Z_n."""
    elements = list(range(n))
    raw_partitions = get_partitions(elements)
    bell_n = len(raw_partitions)
    ops = get_dihedral_ops(n)
    group_order = len(ops)

    # Group raw partitions by shape lambda |- n
    shapes_dict = defaultdict(list)
    for p in raw_partitions:
        p_norm = [sorted(b) for b in p]
        p_norm.sort(key=lambda blk: (min(blk), blk))
        shape = tuple(sorted([len(b) for b in p_norm], reverse=True))
        shapes_dict[shape].append(p_norm)

    sorted_shapes = sorted(shapes_dict.keys(), key=lambda sh: (len(sh), [-x for x in sh]))

    shape_stats = {}
    all_orbits = []

    for shape in sorted_shapes:
        raw_list = shapes_dict[shape]
        p_count = len(raw_list)
        seen_orbits = set()
        shape_orbits = []

        for p in raw_list:
            canon = canonicalise_partition(p, n)
            canon_tup = tuple(tuple(b) for b in canon)
            if canon_tup not in seen_orbits:
                seen_orbits.add(canon_tup)
                orb = get_orbit(canon, n)
                orb_sz = len(orb)

                s_count = sum(1 for b in canon if is_block_symmetric(b, n))
                sig = "".join("s" if is_block_symmetric(b, n) else "c" for b in canon)
                energy = sum(compute_block_energy(b, n) for b in canon)

                shape_orbits.append({
                    'n': n,
                    'shape': shape,
                    'partition': canon,
                    'slash': format_slash(canon),
                    'orbit_size': orb_sz,
                    'stab_size': group_order // orb_sz,
                    's_count': s_count,
                    'sig': sig,
                    'energy': energy,
                })

        # Sort within shape: descending s_count, descending energy, then slash
        shape_orbits.sort(key=lambda o: (-o['s_count'], -o['energy'], o['slash']))
        for i, o in enumerate(shape_orbits, 1):
            o['shape_id'] = i

        orbit_sizes_dist = defaultdict(int)
        for o in shape_orbits:
            orbit_sizes_dist[o['orbit_size']] += 1

        shape_stats[shape] = {
            'partitions_count': p_count,
            'orbits_count': len(shape_orbits),
            'orbit_sizes': dict(orbit_sizes_dist)
        }
        all_orbits.extend(shape_orbits)

    for i, o in enumerate(all_orbits, 1):
        o['local_id'] = i

    return {
        'n': n,
        'group_order': group_order,
        'bell_n': bell_n,
        'total_orbits': len(all_orbits),
        'shape_stats': shape_stats,
        'sorted_shapes': sorted_shapes,
        'orbits': all_orbits
    }

def format_shape_monomial(shape: Tuple[int, ...]) -> str:
    """Format partition shape as polynomial monomial e.g. (2, 2, 1, 1) -> z_2^2 z_1^2."""
    counts = defaultdict(int)
    for p in shape:
        counts[p] += 1
    terms = []
    for p in sorted(counts.keys(), reverse=True):
        c = counts[p]
        if c == 1:
            terms.append(f"z_{p}")
        else:
            terms.append(f"z_{p}^{c}")
    return " ".join(terms)

def format_orbit_poly(orbit_sizes: Dict[int, int]) -> str:
    r"""Format orbit sizes distribution as polynomial e.g. 2\omega^1 + 4\omega^2."""
    terms = []
    for sz in sorted(orbit_sizes.keys()):
        cnt = orbit_sizes[sz]
        terms.append(f"{cnt}\\omega^{{{sz}}}")
    return " + ".join(terms) if terms else "0"

def generate_latex_tables(all_ring_data: Dict[int, Dict[str, Any]], gen_dir: str):
    """Generate LaTeX tables for monograph chapters."""
    os.makedirs(gen_dir, exist_ok=True)

    # 1. Consolidated Census Table (Z_1 to Z_8)
    summary_path = os.path.join(gen_dir, "census_summary_z1_z8.tex")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("% Auto-generated by generate_multilattice_atlas.py\n")
        f.write("\\begin{table}[htbp]\n\\centering\n\\small\n")
        f.write("\\caption{\\label{tab:census-z1-z8}Consolidated Dihedral Mosaic Census from $\\mathbb{Z}_1$ to $\\mathbb{Z}_8$ (OEIS A084708)}\n")
        f.write("\\begin{tabular}{c r r r r l}\n")
        f.write("\\toprule\n")
        f.write("Ring $\\mathbb{Z}_n$ & $|D_n|$ & Partitions $B_n$ & Shapes & Dihedral Mosaics & Orbit Size Decomposition $\\sum a_k \\omega^k$ \\\\\n")
        f.write("\\midrule\n")

        tot_p = 0
        tot_m = 0
        tot_shapes = 0

        for n in range(1, 9):
            rd = all_ring_data[n]
            tot_p += rd['bell_n']
            tot_m += rd['total_orbits']
            tot_shapes += len(rd['sorted_shapes'])

            # Aggregate orbit size distribution for ring n
            agg_sizes = defaultdict(int)
            for sh_info in rd['shape_stats'].values():
                for sz, cnt in sh_info['orbit_sizes'].items():
                    agg_sizes[sz] += cnt
            poly_str = format_orbit_poly(agg_sizes)

            f.write(f"$\\mathbb{{Z}}_{n}$ & {rd['group_order']} & {rd['bell_n']:,} & {len(rd['sorted_shapes'])} & \\textbf{{{rd['total_orbits']}}} & ${poly_str}$ \\\\\n")

        f.write("\\midrule\\midrule\n")
        f.write(f"\\textbf{{Total}} & --- & \\textbf{{{tot_p:,}}} & \\textbf{{{tot_shapes}}} & \\textbf{{{tot_m}}} & --- \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
    print(f"✓ Wrote consolidated census table: {summary_path}")

    # 2. Detailed Shape Statistics Table for each ring (Z_1..Z_7 and Z_8)
    shape_path = os.path.join(gen_dir, "shape_census_z1_z8.tex")
    with open(shape_path, "w", encoding="utf-8") as f:
        f.write("% Auto-generated by generate_multilattice_atlas.py\n")
        f.write("\\begin{longtable}{r r l l}\n")
        f.write("\\caption{\\label{tab:shape-census-z1-z8}Stratified Partition Shape Inventory for $\\mathbb{Z}_1$ through $\\mathbb{Z}_8$}\\\\\n")
        f.write("\\toprule\n")
        f.write("Partitions $\\#p$ & Mosaics $\\#o$ & Partition Shape Monomial $\\mathbf{z}^\\lambda$ & Orbit Polynomial $Q_\\lambda(\\omega)$ \\\\\n")
        f.write("\\midrule\n\\endfirsthead\n")
        f.write("\\caption[]{Stratified Partition Shape Inventory (continued)}\\\\\n")
        f.write("\\toprule\n")
        f.write("Partitions $\\#p$ & Mosaics $\\#o$ & Partition Shape Monomial $\\mathbf{z}^\\lambda$ & Orbit Polynomial $Q_\\lambda(\\omega)$ \\\\\n")
        f.write("\\midrule\n\\endhead\n")
        f.write("\\bottomrule\n\\endfoot\n")

        for n in range(1, 9):
            rd = all_ring_data[n]
            f.write(f"\\midrule\n\\multicolumn{{4}}{{c}}{{\\textbf{{Ring $\\mathbb{{Z}}_{n}$}} ($|D_{n}|={rd['group_order']}$, $B_{n}={rd['bell_n']}$, {rd['total_orbits']} Mosaics)}} \\\\\n\\midrule\n")

            for shape in rd['sorted_shapes']:
                st = rd['shape_stats'][shape]
                sh_mon = format_shape_monomial(shape)
                q_poly = format_orbit_poly(st['orbit_sizes'])
                f.write(f"{st['partitions_count']} & {st['orbits_count']} & ${sh_mon}$ & ${q_poly}$ \\\\\n")

        f.write("\\bottomrule\n\\end{longtable}\n")
    print(f"✓ Wrote detailed shape census table: {shape_path}")

def draw_mosaic_tile(f, o, cx, cy, r=0.62):
    """Draw a single bare mosaic tile without perimeter clutter."""
    n = o['n']
    if n == 1:
        cos_v = [0.0]
        sin_v = [1.0]
    else:
        angles = [math.radians(90.0 - k * (360.0 / n)) for k in range(n)]
        cos_v = [math.cos(a) for a in angles]
        sin_v = [math.sin(a) for a in angles]

    # Ambient wireframe
    if n == 1:
        f.write(f"  \\draw[gray!35, line width=0.25pt] ({cx:.3f},{cy:.3f}) circle ({r:.3f});\n")
    elif n == 2:
        p0 = f"({cx + r * cos_v[0]:.3f},{cy + r * sin_v[0]:.3f})"
        p1 = f"({cx + r * cos_v[1]:.3f},{cy + r * sin_v[1]:.3f})"
        f.write(f"  \\draw[gray!35, line width=0.25pt, dashed] {p0} -- {p1};\n")
    else:
        wire_pts = [f"({cx + r * cos_v[k]:.3f},{cy + r * sin_v[k]:.3f})" for k in range(n)]
        f.write(f"  \\draw[gray!35, line width=0.25pt] {' -- '.join(wire_pts)} -- cycle;\n")

    # Blocks
    for blk in o['partition']:
        is_sym = is_block_symmetric(blk, n)
        col_name = "mosaicblue" if is_sym else "mosaicpink"

        if len(blk) == 1:
            vx = cx + r * cos_v[blk[0]]
            vy = cy + r * sin_v[blk[0]]
            f.write(f"  \\fill[{col_name}!80!black] ({vx:.3f},{vy:.3f}) circle (1.8pt);\n")
        elif len(blk) == 2:
            p1 = f"({cx + r * cos_v[blk[0]]:.3f},{cy + r * sin_v[blk[0]]:.3f})"
            p2 = f"({cx + r * cos_v[blk[1]]:.3f},{cy + r * sin_v[blk[1]]:.3f})"
            f.write(f"  \\draw[{col_name}, line width=2.4pt, line cap=round] {p1} -- {p2};\n")
            f.write(f"  \\draw[black!80, line width=0.4pt, line cap=round] {p1} -- {p2};\n")
        else:
            pts = [f"({cx + r * cos_v[v]:.3f},{cy + r * sin_v[v]:.3f})" for v in blk]
            f.write(f"  \\fill[{col_name}, fill opacity=0.68] {' -- '.join(pts)} -- cycle;\n")
            f.write(f"  \\draw[black!85, line width=0.45pt] {' -- '.join(pts)} -- cycle;\n")

    # NW corner: Local ID number restarting at 1 for each ring
    f.write(f"  \\node[anchor=north west, font=\\footnotesize\\bfseries\\sffamily, text=black!85, inner sep=0pt] at ({cx - 1.15:.3f},{cy + 0.90:.3f}) {{{o['local_id']}}};\n")
    # SE corner: Orbit size |O|
    f.write(f"  \\node[anchor=south east, font=\\scriptsize\\sffamily, text=black!55, inner sep=0pt] at ({cx + 1.15:.3f},{cy - 0.90:.3f}) {{{o['orbit_size']}}};\n")

def generate_visual_plates_tex(all_ring_data: Dict[int, Dict[str, Any]], plate_tex_path: str):
    """Generate high-density TikZ visual plates covering all 509 mosaics."""
    os.makedirs(os.path.dirname(os.path.abspath(plate_tex_path)), exist_ok=True)

    cols = 6
    pitch_x = 2.90
    pitch_y = 2.45
    r = 0.62

    with open(plate_tex_path, "w", encoding="utf-8") as f:
        f.write("% Auto-generated by generate_multilattice_atlas.py - Visual Plates for Z_1..Z_8\n")
        f.write("\\documentclass[11pt,a4paper]{article}\n")
        f.write("\\usepackage[margin=1.2cm]{geometry}\n")
        f.write("\\usepackage{amsmath,amssymb}\n")
        f.write("\\usepackage{tikz}\n")
        f.write("\\usepackage{xcolor}\n")
        f.write("\\definecolor{mosaicblue}{RGB}{74, 128, 196}\n")
        f.write("\\definecolor{mosaicpink}{RGB}{224, 102, 102}\n")
        f.write("\\pagestyle{empty}\n")
        f.write("\\begin{document}\n\n")

        # =========================================================================
        # PLATE 1: Lattices Z_1 through Z_5 (25 mosaics total, cleanly clustered)
        # =========================================================================
        f.write("% Plate Page 1: Lattices Z_1 through Z_5\n")
        f.write("\\noindent\\makebox[\\textwidth][c]{\\begin{tikzpicture}[scale=1.0]\n")

        # Row 0: Z_1 (col 0), Z_2 (cols 1, 2), Z_3 (cols 3, 4, 5)
        f.write(f"  \\node[anchor=south, font=\\footnotesize\\bfseries\\sffamily, text=black!55] at ({0 * pitch_x:.3f}, 1.10) {{$\\mathbb{{Z}}_1$}};\n")
        f.write(f"  \\node[anchor=south, font=\\footnotesize\\bfseries\\sffamily, text=black!55] at ({1.5 * pitch_x:.3f}, 1.10) {{$\\mathbb{{Z}}_2$}};\n")
        f.write(f"  \\node[anchor=south, font=\\footnotesize\\bfseries\\sffamily, text=black!55] at ({4.0 * pitch_x:.3f}, 1.10) {{$\\mathbb{{Z}}_3$}};\n")
        draw_mosaic_tile(f, all_ring_data[1]['orbits'][0], 0 * pitch_x, 0)
        draw_mosaic_tile(f, all_ring_data[2]['orbits'][0], 1 * pitch_x, 0)
        draw_mosaic_tile(f, all_ring_data[2]['orbits'][1], 2 * pitch_x, 0)
        draw_mosaic_tile(f, all_ring_data[3]['orbits'][0], 3 * pitch_x, 0)
        draw_mosaic_tile(f, all_ring_data[3]['orbits'][1], 4 * pitch_x, 0)
        draw_mosaic_tile(f, all_ring_data[3]['orbits'][2], 5 * pitch_x, 0)

        # Rows 1-2: Z_4 (7 mosaics)
        f.write(f"  \\node[anchor=south west, font=\\footnotesize\\bfseries\\sffamily, text=black!55] at ({-1.15:.3f}, {-1 * pitch_y + 1.05:.3f}) {{$\\mathbb{{Z}}_4$}};\n")
        for i in range(6):
            draw_mosaic_tile(f, all_ring_data[4]['orbits'][i], i * pitch_x, -1 * pitch_y)
        draw_mosaic_tile(f, all_ring_data[4]['orbits'][6], 0 * pitch_x, -2 * pitch_y)

        # Rows 3-4: Z_5 (12 mosaics)
        f.write(f"  \\node[anchor=south west, font=\\footnotesize\\bfseries\\sffamily, text=black!55] at ({-1.15:.3f}, {-3 * pitch_y + 1.05:.3f}) {{$\\mathbb{{Z}}_5$}};\n")
        for i in range(6):
            draw_mosaic_tile(f, all_ring_data[5]['orbits'][i], i * pitch_x, -3 * pitch_y)
        for i in range(6):
            draw_mosaic_tile(f, all_ring_data[5]['orbits'][6 + i], i * pitch_x, -4 * pitch_y)

        f.write("\\end{tikzpicture}}\\clearpage\n\n")

        # =========================================================================
        # PLATES 2..10: Pure bare regular grids without hardcoded banner captions
        # =========================================================================
        remaining_batches = [
            ("Lattice Z_6", all_ring_data[6]['orbits']),
            ("Lattice Z_7 Part I", all_ring_data[7]['orbits'][:60]),
            ("Lattice Z_7 Part II", all_ring_data[7]['orbits'][60:]),
            ("Lattice Z_8 Part I", all_ring_data[8]['orbits'][:60]),
            ("Lattice Z_8 Part II", all_ring_data[8]['orbits'][60:120]),
            ("Lattice Z_8 Part III", all_ring_data[8]['orbits'][120:180]),
            ("Lattice Z_8 Part IV", all_ring_data[8]['orbits'][180:240]),
            ("Lattice Z_8 Part V", all_ring_data[8]['orbits'][240:300]),
            ("Lattice Z_8 Part VI", all_ring_data[8]['orbits'][300:]),
        ]

        for batch_title, chunk in remaining_batches:
            f.write(f"% Plate: {batch_title}\n")
            f.write("\\noindent\\makebox[\\textwidth][c]{\\begin{tikzpicture}[scale=1.0]\n")

            for idx_in_page, o in enumerate(chunk):
                col = idx_in_page % cols
                row = idx_in_page // cols
                cx = col * pitch_x
                cy = - (row * pitch_y)
                draw_mosaic_tile(f, o, cx, cy, r)

            f.write("\\end{tikzpicture}}\\clearpage\n\n")

        f.write("\\end{document}\n")
    print(f"✓ Wrote visual plates TikZ source (10 pages): {plate_tex_path}")

def main():
    args = parse_args()
    print("=" * 80)
    print("OCTATLAS: MULTI-LATTICE GENERATOR (Z_1 THROUGH Z_8)")
    print("=" * 80)

    all_ring_data = {}
    global_id_counter = 1

    for n in range(1, args.max_n + 1):
        print(f"\nProcessing cyclic ring Z_{n}...")
        rd = compute_ring_mosaics(n)
        for o in rd['orbits']:
            o['global_id'] = global_id_counter
            global_id_counter += 1
        all_ring_data[n] = rd
        print(f"  Z_{n}: {rd['bell_n']} partitions -> {rd['total_orbits']} dihedral mosaics across {len(rd['sorted_shapes'])} shapes.")

    total_mosaics = global_id_counter - 1
    print("-" * 80)
    print(f"GRAND TOTAL DIHEDRAL COMPOSITION MOSAICS (Z_1..Z_{args.max_n}): {total_mosaics} (Expected: 509)")
    print("-" * 80)

    gen_dir = os.path.join(args.output_dir, "gen")
    plates_dir = os.path.join(args.output_dir, "plates")
    plates_tex_path = os.path.join(plates_dir, "plates_z1_z8.tex")

    generate_latex_tables(all_ring_data, gen_dir)
    generate_visual_plates_tex(all_ring_data, plates_tex_path)
    print("\n✓ Multi-lattice atlas generation complete.")

if __name__ == "__main__":
    main()
