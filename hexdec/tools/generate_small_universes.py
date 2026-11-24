#!/usr/bin/env python3
"""
generate_small_universes.py - Exact Computation and TikZ Generation for Small Universes D_4 and D_9

1. D_4 Universe: z_2^2 on Z_4
   - 2 Monomers (M_1, M_2)
2. D_9 Universe: z_3^3 on Z_9
   - 1 Monomer (M_1)
   - 8 Trimers (T_1 .. T_8, 3-cycles under mu_2: x -> 2x)

Author: Gemma Knee
"""

import sys
import os
import math
import itertools
from typing import List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def get_d_elements(n):
    return [(a, b) for a in [1, n - 1] for b in range(n)]

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

def get_polygon_vertex_coords(cx: float, cy: float, r: float, n: int) -> List[Tuple[float, float]]:
    coords = []
    step = 360.0 / n
    for k in range(n):
        angle = math.radians(90.0 - k * step)
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return coords

def render_polygon_mosaic_tikz(cx: float, cy: float, r: float, blocks: list, n: int, is_chord_only: bool = False) -> List[str]:
    lines = []
    coords = get_polygon_vertex_coords(cx, cy, r, n)

    # Wireframe n-gon boundary
    path = " -- ".join(f"({x:.2f},{y:.2f})" for x, y in coords) + " -- cycle"
    lines.append(f"    \\draw[gray!40, line width=0.25pt] {path};")

    for blk in blocks:
        s_blk = sorted(list(blk))
        sym = is_block_symmetric(s_blk, n)
        col_name = "mosaicblue" if sym else "mosaicpink"
        if is_chord_only:
            # For 2-point blocks (Z_4), draw thick chord
            v1, v2 = s_blk
            lines.append(f"    \\draw[{col_name}!80!black, line width=1.1pt] ({coords[v1][0]:.2f},{coords[v1][1]:.2f}) -- ({coords[v2][0]:.2f},{coords[v2][1]:.2f});")
        else:
            corners = " -- ".join(f"({coords[v][0]:.2f},{coords[v][1]:.2f})" for v in s_blk) + " -- cycle"
            lines.append(f"    \\fill[{col_name}, fill opacity=0.62] {corners};")
            lines.append(f"    \\draw[black!85, line width=0.35pt] {corners};")

    return lines

# ----------------------------------------------------------------------
# 1. D_4 Universe (z_2^2 on Z_4)
# ----------------------------------------------------------------------
def generate_d4_tikz(output_path: str):
    m1 = [[0, 2], [1, 3]]
    m2 = [[0, 1], [2, 3]]
    monomers = [(m1, 1), (m2, 2)]

    lines = []
    lines.append("% TikZ Plate: The Complete D_4 Universe (z_2^2 on Z_4)")
    lines.append("% 2 Monomers: M_1 (cross, |O|=1) and M_2 (parallel chords, |O|=2)")
    lines.append("\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=1.0]")

    r = 0.90
    dx = 4.20
    for idx, (p, sz) in enumerate(monomers):
        cx = 2.50 + idx * dx
        cy = 0.0
        bx1 = cx - 1.45
        bx2 = cx + 1.45
        by1 = -1.35
        by2 = 1.35

        lines.append(f"\n  % --- Monomer M{idx+1} ---")
        lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=6pt, line width=0.45pt] ({bx1:.2f}, {by1:.2f}) rectangle ({bx2:.2f}, {by2:.2f});")
        lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=2pt, inner sep=1.8pt, font=\\small\\bfseries\\sffamily] at ({bx1 + 0.18:.2f}, {by2:.2f}) {{{idx+1}}};")
        lines.append(f"  \\node[anchor=east, font=\\tiny\\color{{black!55}}] at ({bx2 - 0.20:.2f}, {by1 + 0.20:.2f}) {{{sz}}};")

        lines.extend(render_polygon_mosaic_tikz(cx, cy, r, p, 4, is_chord_only=True))

    lines.append("\\end{tikzpicture}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ Generated D_4 universe TikZ at {output_path}")

# ----------------------------------------------------------------------
# 2. D_9 Universe (z_3^3 on Z_9)
# ----------------------------------------------------------------------
def generate_d9_tikz(output_path: str):
    # Monomer M1: regular triangles coset partition
    m1 = [[0, 3, 6], [1, 4, 7], [2, 5, 8]]

    # 8 Trimers
    trimers = [
        # T1: |O|=3, s=3, E=99
        ([[0, 1, 5], [2, 6, 7], [3, 4, 8]], [[0, 1, 2], [3, 4, 5], [6, 7, 8]], [[0, 2, 4], [1, 6, 8], [3, 5, 7]], 3),
        # T2: |O|=9, s=3, E=90
        ([[0, 1, 5], [2, 3, 7], [4, 6, 8]], [[0, 1, 2], [3, 7, 8], [4, 5, 6]], [[0, 2, 4], [1, 3, 8], [5, 6, 7]], 9),
        # T3: |O|=9, s=1, E=91
        ([[0, 1, 5], [2, 4, 7], [3, 6, 8]], [[0, 1, 2], [3, 6, 7], [4, 5, 8]], [[0, 2, 4], [1, 7, 8], [3, 5, 6]], 9),
        # T4: |O|=9, s=1, E=85
        ([[0, 1, 4], [2, 5, 6], [3, 7, 8]], [[0, 2, 8], [1, 3, 4], [5, 6, 7]], [[0, 4, 7], [1, 3, 5], [2, 6, 8]], 9),
        # T5: |O|=9, s=1, E=85
        ([[0, 2, 5], [1, 4, 7], [3, 6, 8]], [[0, 1, 4], [2, 5, 8], [3, 6, 7]], [[0, 2, 8], [1, 4, 7], [3, 5, 6]], 9),
        # T6: |O|=18, s=1, E=88
        ([[0, 1, 4], [2, 6, 7], [3, 5, 8]], [[0, 2, 8], [1, 6, 7], [3, 4, 5]], [[0, 4, 7], [1, 6, 8], [2, 3, 5]], 18),
        # T7: |O|=18, s=1, E=79
        ([[0, 1, 4], [2, 6, 8], [3, 5, 7]], [[0, 2, 8], [1, 5, 6], [3, 4, 7]], [[0, 4, 7], [1, 2, 3], [5, 6, 8]], 18),
        # T8: |O|=18, s=0, E=84 (all chiral)
        ([[0, 1, 4], [2, 5, 7], [3, 6, 8]], [[0, 2, 8], [1, 4, 5], [3, 6, 7]], [[0, 4, 7], [1, 2, 8], [3, 5, 6]], 18),
    ]

    lines = []
    lines.append("% TikZ Plate: The Complete D_9 Universe (z_3^3 on Z_9)")
    lines.append("% 1 Monomer (M_1) and 8 Trimers (T_1 .. T_8, 3-cycles under mu_2)")
    lines.append("\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=1.0]")

    # 1. Monomer M1 at top center
    r_mono = 0.95
    cx_m = 7.50
    cy_m = 0.0
    bx1 = cx_m - 1.55
    bx2 = cx_m + 1.55
    by1 = cy_m - 1.40
    by2 = cy_m + 1.40

    lines.append("\n  % --- Monomer M1 ---")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at (0.0, {cy_m + 1.85:.2f}) {{I. The Sole Monomer ($M_1$, $|O|=1$)}};")
    lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=6pt, line width=0.45pt] ({bx1:.2f}, {by1:.2f}) rectangle ({bx2:.2f}, {by2:.2f});")
    lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=2pt, inner sep=1.8pt, font=\\small\\bfseries\\sffamily] at ({bx1 + 0.18:.2f}, {by2:.2f}) {{1}};")
    lines.append(f"  \\node[anchor=east, font=\\tiny\\color{{black!55}}] at ({bx2 - 0.20:.2f}, {by1 + 0.20:.2f}) {{1}};")
    lines.extend(render_polygon_mosaic_tikz(cx_m, cy_m, r_mono, m1, 9))

    # 2. Trimers T1..T8 arranged as 4 rows of 2 linear 3-strips
    r_trimer = 0.62
    d_inner = 1.55
    pad_x = 0.75
    pad_y = 0.60
    w_half = d_inner + pad_x # 1.55 + 0.75 = 2.30 cm -> box width 4.60 cm
    h_half = r_trimer + pad_y # 0.62 + 0.60 = 1.22 cm -> box height 2.44 cm

    lines.append("\n  % --- The 8 Trimers (3-Cycles: mu_1 -> mu_2 -> mu_4) ---")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at (0.0, {-2.35:.2f}) {{II. The Complete Catalogue of 8 Trimers ($T_1 \\dots T_8$, 3-Cycles: $\\mu_1 \\to \\mu_2 \\to \\mu_4$)}};")

    dx_col = 7.50
    x_centers = [3.75, 11.25]
    y_start = -4.00
    dy_row = 2.80

    for idx, (p1, p2, p3, sz) in enumerate(trimers):
        col = idx % 2
        row = idx // 2
        cx = x_centers[col]
        cy = y_start - row * dy_row

        bx1 = cx - w_half
        bx2 = cx + w_half
        by1 = cy - h_half
        by2 = cy + h_half

        lines.append(f"\n  % --- Trimer #{idx+1} (|O|={sz}) ---")
        lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=5pt, line width=0.45pt] ({bx1:.2f}, {by1:.2f}) rectangle ({bx2:.2f}, {by2:.2f});")
        lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=2pt, inner sep=1.5pt, font=\\scriptsize\\bfseries\\sffamily] at ({bx1 + 0.16:.2f}, {by2:.2f}) {{{idx+1}}};")
        lines.append(f"  \\node[anchor=east, font=\\tiny\\color{{black!55}}] at ({bx2 - 0.18:.2f}, {by1 + 0.18:.2f}) {{{sz}}};")

        # 3 mosaics: mu_1, mu_2, mu_4
        for step, part in enumerate([p1, p2, p3]):
            mx = cx - d_inner + step * d_inner
            my = cy
            lines.extend(render_polygon_mosaic_tikz(mx, my, r_trimer, part, 9))

    lines.append("\\end{tikzpicture}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ Generated D_9 universe TikZ at {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate TikZ plates for small universes D_4 and D_9.")
    default_dir = os.path.join(os.path.dirname(__file__), "..", "tkz")
    parser.add_argument("-d", "--out-dir", type=str, default=default_dir, help=f"Output directory (default: {default_dir})")
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    out_d4 = os.path.join(args.out_dir, "fig_d4_universe.tkz")
    out_d9 = os.path.join(args.out_dir, "fig_d9_universe.tkz")
    generate_d4_tikz(out_d4)
    generate_d9_tikz(out_d9)
