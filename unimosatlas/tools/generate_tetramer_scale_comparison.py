#!/usr/bin/env python3
"""
generate_tetramer_scale_comparison.py - Generate Comparative TikZ Plate for Tetramer Publishing Densities

Renders the first 12 Tetramers as horizontal linear cartouches (1x4 strip: mu_1 -> mu_3 -> mu_7 -> mu_5)
across three publishing scale models:
  Tier 1 (Micro-Atlas, 220-pp model, 96/page): Tetramers 1..4 (dia = 7.0 mm)
  Tier 2 (Luxury Monograph, 432-pp model, 48/page): Tetramers 5..8 (dia = 10.6 mm)
  Tier 3 (Gold-Tooled Leather-Bound, 864-pp model, 24/page): Tetramers 9..12 (dia = 15.6 mm)

Author: Gemma Knee
"""

import sys
import os
import math
import argparse
from typing import List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import get_fixed_partitions
from unimosatlas.tools.mosaic_sorting import (
    is_block_symmetric,
    compute_mosaic_chord_energy,
    get_block_canonical_stride,
)

def extract_high_symmetry_tetramers(n=16, k=4, s=4):
    d_n_elements = [(a, b) for a in [1, 15] for b in range(16)]

    def apply_d(part, a, b):
        return frozenset(frozenset((a * x + b) % n for x in blk) for blk in part)

    def apply_mu(part, mult):
        return frozenset(frozenset((mult * x) % n for x in blk) for blk in part)

    order2_elements = [(1, 8)] + [(15, b) for b in range(16)]
    all_fixed = set()
    for a, b in order2_elements:
        perm = [(a * x + b) % n for x in range(n)]
        pts = get_fixed_partitions(perm, 4, 4)
        all_fixed.update(pts)

    orbits = {}
    visited = set()
    for p in all_fixed:
        if p in visited:
            continue
        orb = frozenset(apply_d(p, a, b) for a, b in d_n_elements)
        visited.update(orb)
        orbits[orb] = len(orb)

    visited_orbs = set()
    tetramers = []

    for o, sz in orbits.items():
        if o in visited_orbs:
            continue
        rep = sorted(list(o), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        rep_mu3 = apply_mu(rep, 3)
        o2 = frozenset(apply_d(rep_mu3, a, b) for a, b in d_n_elements)
        if o2 == o:
            continue
        rep_mu9 = apply_mu(rep_mu3, 3)
        o3 = frozenset(apply_d(rep_mu9, a, b) for a, b in d_n_elements)
        if o3 == o:
            continue
        rep_mu27 = apply_mu(rep_mu9, 3)
        o4 = frozenset(apply_d(rep_mu27, a, b) for a, b in d_n_elements)

        visited_orbs.add(o)
        visited_orbs.add(o2)
        visited_orbs.add(o3)
        visited_orbs.add(o4)

        # For each of the 4 orbits, find canonical cycle where p1 has highest symmetry/energy
        candidate_cycles = []
        for cand_o in [o, o2, o3, o4]:
            c_rep = sorted(list(cand_o), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
            cp1 = [sorted(list(b)) for b in c_rep]
            cp2 = sorted([sorted([(3 * x) % 16 for x in b]) for b in cp1])
            cp3 = sorted([sorted([(7 * x) % 16 for x in b]) for b in cp1])
            cp4 = sorted([sorted([(5 * x) % 16 for x in b]) for b in cp1])

            s_count = sum(1 for b in cp1 if is_block_symmetric(b, 16))
            e = compute_mosaic_chord_energy(cp1, 16)
            strides = tuple(sorted(get_block_canonical_stride(b, 16) for b in cp1))
            key = (sz, -s_count, -e, strides, tuple(tuple(b) for b in cp1))
            candidate_cycles.append((key, (cp1, cp2, cp3, cp4)))

        candidate_cycles.sort(key=lambda x: x[0])
        best_key, best_cycle = candidate_cycles[0]
        tetramers.append((best_key, best_cycle, sz))

    tetramers.sort(key=lambda x: x[0])
    return tetramers

def get_hexadecagon_vertex_coords(cx: float, cy: float, r: float) -> List[Tuple[float, float]]:
    """Return the 16 (x, y) coordinates of regular hexadecagon with vertex 0 at 90 deg."""
    coords = []
    for k in range(16):
        angle = math.radians(90.0 - k * 22.5)
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return coords

def render_mosaic_tikz(cx: float, cy: float, r: float, blocks: list) -> List[str]:
    """Render a single hexadecagon mosaic at (cx, cy) with radius r (dotless)."""
    lines = []
    coords = get_hexadecagon_vertex_coords(cx, cy, r)

    # Background hexadecagon wireframe
    hex_path = " -- ".join(f"({x:.2f},{y:.2f})" for x, y in coords) + " -- cycle"
    lines.append(f"    \\draw[gray!40, line width=0.25pt] {hex_path};")

    # Inscribed convex blocks (strictly circular vertex order, no dots)
    for blk in blocks:
        s_blk = sorted(list(blk))
        sym = is_block_symmetric(s_blk, 16)
        col_name = "mosaicblue" if sym else "mosaicpink"
        corners = " -- ".join(f"({coords[v][0]:.2f},{coords[v][1]:.2f})" for v in s_blk) + " -- cycle"
        lines.append(f"    \\fill[{col_name}, fill opacity=0.62] {corners};")
        lines.append(f"    \\draw[black!85, line width=0.35pt] {corners};")

    return lines

def render_linear_cartouche(cx: float, cy: float, t_num: int, orb_sz: int,
                            cycle: list, r: float, d_inner: float, pad_x: float, pad_y: float,
                            font_badge: str = "\\scriptsize") -> List[str]:
    """
    Render a 1x4 horizontal linear cartouche centered at (cx, cy).
    The 4 mosaics are placed left-to-right:
      Pos 0: p1 (mu1, root)
      Pos 1: p2 (mu3, 1st dilation)
      Pos 2: p3 (mu7, involution)
      Pos 3: p4 (mu5, inverse)
    """
    lines = []
    w_half = 1.5 * d_inner + pad_x
    h_half = r + pad_y

    x_min = cx - w_half
    x_max = cx + w_half
    y_min = cy - h_half
    y_max = cy + h_half

    # Rounded cartouche frame
    lines.append(f"  % Cartouche T{t_num:05d} (|O|={orb_sz})")
    lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=3.5pt, line width=0.45pt] ({x_min:.2f}, {y_min:.2f}) rectangle ({x_max:.2f}, {y_max:.2f});")

    # Minimalist identification badge
    badge_x = x_min + 0.22
    lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=2pt, inner sep=1.4pt, font={font_badge}\\bfseries\\sffamily] at ({badge_x:.2f}, {y_max:.2f}) {{{t_num}}};")

    # Render 4 mosaics at x-offsets: -1.5*d, -0.5*d, +0.5*d, +1.5*d
    offsets = [-1.5 * d_inner, -0.5 * d_inner, 0.5 * d_inner, 1.5 * d_inner]
    for step in range(4):
        mx = cx + offsets[step]
        lines.extend(render_mosaic_tikz(mx, cy, r, cycle[step]))

    return lines

def generate_comparison_plate(output_path: str):
    tetramers = extract_high_symmetry_tetramers()
    print(f"Extracted {len(tetramers)} high-symmetry tetramers. Generating linear comparison plate...")

    lines = []
    lines.append("% TikZ Plate: Comparative Publishing Scales for Linear Tetramer Cartouches")
    lines.append("% Author: Gemma Knee & Antigra Vitti (November 2026)")
    lines.append("\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=0.96]")

    x_left_label = 0.0
    x_right_label = 15.0

    # -------------------------------------------------------------
    # TIER 1: Micro-Atlas (220-page model)
    # -------------------------------------------------------------
    r1 = 0.35
    d_inner1 = 0.82
    pad_x1 = 0.45
    pad_y1 = 0.28

    lines.append("  % ==========================================================")
    lines.append("  % TIER 1: Micro-Atlas Model (220 Pages, 96 Tetramers / Page)")
    lines.append("  % Tetramers 1..4 (Diameter = 7.0 mm, Linear 1x4 Strip)")
    lines.append("  % ==========================================================")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at ({x_left_label:.2f}, 0.55) {{I. Compact Reference Atlas Model (220 pp, 96/page, $\\varnothing = 7.0\\text{{ mm}}$, linear strip)}};")
    lines.append(f"  \\node[anchor=east, font=\\itshape\\scriptsize, color=black!60] at ({x_right_label:.2f}, 0.55) {{Tetramers $T_1 \\dots T_4$ ($|O|=4$)}};")

    x_start1 = 1.85
    dx1 = 3.75
    y1 = -0.55
    for idx in range(4):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start1 + idx * dx1
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y1, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r1, d_inner=d_inner1, pad_x=pad_x1, pad_y=pad_y1, font_badge="\\tiny"
        ))

    # -------------------------------------------------------------
    # TIER 2: Luxury Monograph (432-page model)
    # -------------------------------------------------------------
    r2 = 0.53
    d_inner2 = 1.25
    pad_x2 = 0.65
    pad_y2 = 0.42

    lines.append("\n  % ==========================================================")
    lines.append("  % TIER 2: Luxury Monograph Model (432 Pages, 48 Tetramers / Page)")
    lines.append("  % Tetramers 5..8 (Diameter = 10.6 mm, Linear 1x4 Strip)")
    lines.append("  % ==========================================================")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at ({x_left_label:.2f}, -2.45) {{II. Luxury Monograph Model (432 pp, 48/page, $\\varnothing = 10.6\\text{{ mm}}$, linear strip)}};")
    lines.append(f"  \\node[anchor=east, font=\\itshape\\scriptsize, color=black!60] at ({x_right_label:.2f}, -2.45) {{Tetramers $T_5 \\dots T_8$ ($|O|=4$)}};")

    x_start2 = 2.75
    dx2 = 5.50
    # Row 1 of Tier 2: T5, T6
    y2_r1 = -3.95
    for i, idx in enumerate([4, 5]):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start2 + i * dx2
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y2_r1, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r2, d_inner=d_inner2, pad_x=pad_x2, pad_y=pad_y2, font_badge="\\scriptsize"
        ))

    # Row 2 of Tier 2: T7, T8
    y2_r2 = -6.15
    for i, idx in enumerate([6, 7]):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start2 + i * dx2
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y2_r2, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r2, d_inner=d_inner2, pad_x=pad_x2, pad_y=pad_y2, font_badge="\\scriptsize"
        ))

    # -------------------------------------------------------------
    # TIER 3: Gold-Tooled Leather-Bound (864-page model)
    # -------------------------------------------------------------
    r3 = 0.75
    d_inner3 = 1.75
    pad_x3 = 0.85
    pad_y3 = 0.70

    lines.append("\n  % ==========================================================")
    lines.append("  % TIER 3: Gold-Tooled Leather-Bound Model (864 Pages, 24 Tetramers / Page)")
    lines.append("  % Tetramers 9..12 (Diameter = 15.0 mm, Linear 1x4 Strip)")
    lines.append("  % ==========================================================")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at ({x_left_label:.2f}, -8.45) {{III. Gold-Tooled Leather-Bound Model (864 pp, 24/page, $\\varnothing = 15.0\\text{{ mm}}$, linear strip)}};")
    lines.append(f"  \\node[anchor=east, font=\\itshape\\scriptsize, color=black!60] at ({x_right_label:.2f}, -8.45) {{Tetramers $T_9 \\dots T_{12}$ ($|O|=8$)}};")

    x_start3 = 3.75
    dx3 = 7.50
    # Row 1 of Tier 3: T9, T10
    y3_r1 = -10.35
    for i, idx in enumerate([8, 9]):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start3 + i * dx3
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y3_r1, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r3, d_inner=d_inner3, pad_x=pad_x3, pad_y=pad_y3, font_badge="\\small"
        ))

    # Row 2 of Tier 3: T11, T12
    y3_r2 = -13.60
    for i, idx in enumerate([10, 11]):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start3 + i * dx3
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y3_r2, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r3, d_inner=d_inner3, pad_x=pad_x3, pad_y=pad_y3, font_badge="\\small"
        ))

    lines.append("\\end{tikzpicture}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ Generated linear tetramer comparison plate at {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate comparative TikZ plate for publishing densities of linear tetramer cartouches."
    )
    default_out = os.path.join(os.path.dirname(__file__), "..", "tkz", "fig_tetramer_scale_comparison.tkz")
    parser.add_argument(
        "-o", "--out",
        type=str,
        default=default_out,
        help=f"Output path for generated TikZ file (default: {default_out})"
    )
    args = parser.parse_args()
    generate_comparison_plate(args.out)

if __name__ == "__main__":
    main()
