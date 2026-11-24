#!/usr/bin/env python3
"""
generate_dimers_plates.py - Generate TikZ plates for the 295 Dimers of z_4^4 on Z_16

Arranges the 295 dimers in vertical bi-cartouches (top mosaic = higher energy / canonical rep, bottom = Galois conjugate).
Sorted strictly by the 5-tier natural geometric cascade:
1. Dihedral orbit size |O| (ascending: 2 -> 4 -> 8 -> 16 -> 32)
2. Symmetric block count s (descending: 4 -> 3 -> 2 -> 1 -> 0)
3. Chord dispersion energy max(E_top, E_bot) descending
4. Canonical stride profile multiset
5. Canonical lexicographical tie-breaker

Layout:
  5 columns x 5 rows = 25 dimers per page (12 pages: 11 pages of 25, 1 page of 20).
  Because 295 = 5 * 59, EVERY row on EVERY page has exactly 5 dimers.

Author: Gemma Knee
"""

import sys
import os
import json
import math
import argparse
from typing import List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from hexdec.tools.extract_doublets import extract_all_doublets
from hexdec.tools.mosaic_sorting import (
    is_block_symmetric,
    compute_mosaic_chord_energy,
    get_block_canonical_stride,
)

def get_hexadecagon_vertex_coords(cx: float, cy: float, r: float) -> List[Tuple[float, float]]:
    """Return the 16 (x, y) coordinates of regular hexadecagon with vertex 0 at 90 deg."""
    coords = []
    for k in range(16):
        angle = math.radians(90.0 - k * 22.5)
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return coords

def load_and_sort_dimers(cache_file: str) -> list:
    """Load dimers from JSON cache, orient top/bottom, and sort by 5-tier cascade."""
    if not os.path.exists(cache_file):
        print("Extracting doublets from group action...")
        extract_all_doublets(16, 4, 4)

    with open(cache_file, "r") as f:
        data = json.load(f)

    sorted_dimers = []
    for item in data:
        p1 = [sorted(list(b)) for b in item["p1"]]
        p2 = [sorted(list(b)) for b in item["p2"]]
        sz = item["sz1"]
        
        s1 = sum(1 for b in p1 if is_block_symmetric(b, 16))
        e1 = compute_mosaic_chord_energy(p1, 16)
        e2 = compute_mosaic_chord_energy(p2, 16)

        # Orient higher energy on top; use canonical tie-breaker if equal
        if e1 > e2:
            top_p, bot_p = p1, p2
        elif e2 > e1:
            top_p, bot_p = p2, p1
        else:
            if p1 <= p2:
                top_p, bot_p = p1, p2
            else:
                top_p, bot_p = p2, p1

        e_top = max(e1, e2)
        e_bot = min(e1, e2)
        strides = tuple(sorted(get_block_canonical_stride(b, 16) for b in top_p))
        key = (sz, -s1, -e_top, -e_bot, strides, tuple(tuple(b) for b in top_p))
        sorted_dimers.append((key, top_p, bot_p, sz, s1, e_top, e_bot))

    sorted_dimers.sort(key=lambda x: x[0])
    return sorted_dimers

def render_mosaic_tikz(cx: float, cy: float, r: float, blocks: list) -> List[str]:
    """Render a single hexadecagon mosaic at (cx, cy) with radius r."""
    lines = []
    coords = get_hexadecagon_vertex_coords(cx, cy, r)

    # Draw background polygon boundary
    hex_path = " -- ".join(f"({x:.2f},{y:.2f})" for x, y in coords) + " -- cycle"
    lines.append(f"    \\draw[gray!45, line width=0.30pt] {hex_path};")

    # Draw blocks with vertices in cyclic circular order (strictly convex, no self-intersection)
    for blk in blocks:
        s_blk = sorted(list(blk))
        sym = is_block_symmetric(s_blk, 16)
        col_name = "mosaicblue" if sym else "mosaicpink"
        corners = " -- ".join(f"({coords[v][0]:.2f},{coords[v][1]:.2f})" for v in s_blk) + " -- cycle"
        lines.append(f"    \\fill[{col_name}, fill opacity=0.62] {corners};")
        lines.append(f"    \\draw[black!85, line width=0.40pt] {corners};")

    return lines

def generate_page_tikz(dimers_slice: list, start_idx: int, cols: int = 5,
                       r: float = 0.78, dx: float = 3.48, dy_row: float = 4.60,
                       scale: float = 0.95) -> str:
    """Generate TikZ code for a single plate of vertical bi-cartouches."""
    lines = []
    lines.append(f"% TikZ Plate: Dimers {start_idx} to {start_idx + len(dimers_slice) - 1}")
    lines.append(f"\\begin{{tikzpicture}}[>=latex, line join=round, line cap=round, scale={scale:.2f}]")

    # Vertical bi-cartouche dimensions
    dy_inner = 1.85
    pad_x = 1.25
    pad_y = 1.05
    w_half = pad_x
    h_top = dy_inner / 2.0 + pad_y
    h_bot = -dy_inner / 2.0 - pad_y

    for idx, (key, top_p, bot_p, sz, s_cnt, e_top, e_bot) in enumerate(dimers_slice):
        d_num = start_idx + idx
        col = idx % cols
        row = idx // cols

        # Center of the bi-cartouche
        cx = col * dx
        cy = -row * dy_row

        # Bi-cartouche box
        bx1 = cx - w_half
        bx2 = cx + w_half
        by1 = cy + h_bot
        by2 = cy + h_top

        lines.append(f"\n  % --- Bi-Cartouche #{d_num} (Orbit size {sz}, Sym {s_cnt}, Energy {e_top}/{e_bot}) ---")
        lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=6pt, line width=0.50pt] ({bx1:.2f}, {by1:.2f}) rectangle ({bx2:.2f}, {by2:.2f});")

        # Top-left badge: dimer integer
        lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=2.5pt, inner sep=1.8pt, font=\\scriptsize\\bfseries\\sffamily] at ({bx1 + 0.18:.2f}, {by2:.2f}) {{{d_num}}};")

        # Bottom-right badge: orbit size
        lines.append(f"  \\node[anchor=east, font=\\tiny\\color{{black!55}}] at ({bx2 - 0.20:.2f}, {by1 + 0.22:.2f}) {{{sz}}};")

        # Top mosaic: O_a
        top_cy = cy + dy_inner / 2.0
        lines.extend(render_mosaic_tikz(cx, top_cy, r, top_p))

        # Bottom mosaic: O_b
        bot_cy = cy - dy_inner / 2.0
        lines.extend(render_mosaic_tikz(cx, bot_cy, r, bot_p))

    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate TikZ plates for the 295 Dimers.")
    parser.add_argument("--cols", type=int, default=5, help="Columns per page (default: 5)")
    parser.add_argument("--rows", type=int, default=5, help="Rows per page (default: 5)")
    parser.add_argument("--outdir", default="hexdec/tkz/dimers", help="Output directory for TikZ files")
    parser.add_argument("--scale", type=float, default=0.95, help="TikZ scale (default: 0.95)")
    args = parser.parse_args()

    cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "doublets.json")
    dimers = load_and_sort_dimers(cache_path)

    per_page = args.cols * args.rows
    total_pages = math.ceil(len(dimers) / per_page)

    print(f"Generating TikZ plates for {len(dimers)} dimers:")
    print(f"  Layout: {args.cols} cols x {args.rows} rows = {per_page} per page")
    print(f"  Total pages: {total_pages}")
    print(f"  Output directory: {args.outdir}")

    os.makedirs(args.outdir, exist_ok=True)

    # Master LaTeX inclusion file
    plate_tex_lines = []
    plate_tex_lines.append("% Master inclusion file for all Dimer plates")
    plate_tex_lines.append("\\section{The Complete Catalogue of 295 Dimers}")
    plate_tex_lines.append("\\label{sec:dimers-catalogue}")
    plate_tex_lines.append("")
    plate_tex_lines.append("Each vertical bi-cartouche contains an affine dimer $\\{O_a, O_b\\}$ of shape $z_4^4$ on $\\mathbb{Z}_{16}$, paired under the Galois multiplier $\\mu_3 \\colon x \\mapsto 3x$ (top to bottom). The top mosaic is canonically chosen as the member of the pair exhibiting higher chord dispersion energy (greater regularity). The top-left badge identifies the dimer index ($1, \\dots, 295$); the small bottom-right numeral notes the shared dihedral orbit size $|O| \\in \\{2, 4, 8, 16, 32\\}$.")
    plate_tex_lines.append("")

    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * per_page + 1
        end_idx = min(page_num * per_page, len(dimers))
        dimers_slice = dimers[(start_idx - 1):end_idx]

        filename = f"plate_dimers_{page_num:02d}.tkz"
        filepath = os.path.join(args.outdir, filename)

        tikz_content = generate_page_tikz(
            dimers_slice=dimers_slice,
            start_idx=start_idx,
            cols=args.cols,
            scale=args.scale,
        )

        with open(filepath, "w") as f:
            f.write(tikz_content)

        print(f"  [Page {page_num:2d}/{total_pages:2d}] Dimers {start_idx:3d}..{end_idx:3d} ({len(dimers_slice):2d} bi-cartouches) -> {filename}")

        plate_tex_lines.append("\\begin{figure}[p]")
        plate_tex_lines.append("\\centering")
        plate_tex_lines.append(f"\\input{{tkz/dimers/{filename}}}")
        plate_tex_lines.append(f"\\caption{{Dimers {start_idx} to {end_idx}}}")
        plate_tex_lines.append("\\end{figure}")
        plate_tex_lines.append("\\clearpage")
        plate_tex_lines.append("")

    master_path = os.path.join(os.path.dirname(__file__), "..", "sec", "DimersCatalogue.tex")
    with open(master_path, "w") as f:
        f.write("\n".join(plate_tex_lines))
    print(f"✓ Master catalogue file written to {master_path}")

if __name__ == "__main__":
    main()
