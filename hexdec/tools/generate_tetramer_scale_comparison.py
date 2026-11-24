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
from typing import List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from hexdec.tools.inspect_first_tetramers import extract_high_symmetry_tetramers
from hexdec.tools.mosaic_sorting import is_block_symmetric

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

    bx1 = cx - w_half
    bx2 = cx + w_half
    by1 = cy - h_half
    by2 = cy + h_half

    lines.append(f"\n  % --- Linear Cartouche #{t_num} (|O|={orb_sz}) ---")
    lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=5pt, line width=0.45pt] ({bx1:.2f}, {by1:.2f}) rectangle ({bx2:.2f}, {by2:.2f});")

    # Badges
    lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=2pt, inner sep=1.5pt, font={font_badge}\\bfseries\\sffamily] at ({bx1 + 0.14:.2f}, {by2:.2f}) {{{t_num}}};")
    lines.append(f"  \\node[anchor=east, font=\\tiny\\color{{black!55}}] at ({bx2 - 0.16:.2f}, {by1 + 0.16:.2f}) {{{orb_sz}}};")

    # Mosaics left-to-right
    for step in range(4):
        mx = cx - 1.5 * d_inner + step * d_inner
        my = cy
        p = cycle[step]
        lines.extend(render_mosaic_tikz(mx, my, r, p))

    return lines

def generate_comparison_plate(output_path: str):
    tetramers = extract_high_symmetry_tetramers()
    print(f"Extracted {len(tetramers)} high-symmetry tetramers. Generating linear comparison plate...")

    lines = []
    lines.append("% TikZ Plate: Tetramer Publishing Scale Comparison (Linear 1x4 Strips)")
    lines.append("% Strictly left-to-right: mu_1 -> mu_3 -> mu_7 -> mu_5")
    lines.append("\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=1.0]")

    x_left_label = 0.0
    x_right_label = 15.0

    # -------------------------------------------------------------
    # TIER 1: Micro-Atlas (220-page model, 96 tetramers/page)
    # 4 cartouches side by side: T1..T4
    # r = 0.35 cm (dia = 7.0 mm), d_inner = 0.80 cm, pad_x = 0.42 cm, pad_y = 0.40 cm
    # Box width = 3 * 0.80 + 0.84 = 3.24 cm
    # Pitch dx = 3.75 cm
    # -------------------------------------------------------------
    r1 = 0.35
    d_inner1 = 0.80
    pad_x1 = 0.42
    pad_y1 = 0.40
    y1 = 0.0

    lines.append("\n  % ==========================================================")
    lines.append("  % TIER 1: Micro-Atlas Model (220 Pages, 96 Tetramers / Page)")
    lines.append("  % Tetramers 1..4 (Diameter = 7.0 mm, Linear 1x4 Strip)")
    lines.append("  % ==========================================================")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at ({x_left_label:.2f}, {y1 + 1.15:.2f}) {{I. Micro-Atlas Model (220 pp, 96/page, $\\varnothing = 7.0\\text{{ mm}}$, linear strip)}};")
    lines.append(f"  \\node[anchor=east, font=\\itshape\\scriptsize, color=black!60] at ({x_right_label:.2f}, {y1 + 1.15:.2f}) {{Tetramers $T_1 \\dots T_4$ ($|O|=4, 8$)}};")

    x_start1 = 1.88
    dx1 = 3.75
    for idx in range(4):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start1 + idx * dx1
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y1, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r1, d_inner=d_inner1, pad_x=pad_x1, pad_y=pad_y1, font_badge="\\scriptsize"
        ))

    # -------------------------------------------------------------
    # TIER 2: Luxury Monograph (432-page model, 48 tetramers/page)
    # 4 cartouches in 2 rows of 2: T5..T8
    # r = 0.53 cm (dia = 10.6 mm), d_inner = 1.30 cm, pad_x = 0.65 cm, pad_y = 0.55 cm
    # Box width = 3 * 1.30 + 1.30 = 5.20 cm
    # Pitch dx = 7.50 cm
    # -------------------------------------------------------------
    r2 = 0.53
    d_inner2 = 1.30
    pad_x2 = 0.65
    pad_y2 = 0.55

    lines.append("\n  % ==========================================================")
    lines.append("  % TIER 2: Luxury Monograph Model (432 Pages, 48 Tetramers / Page)")
    lines.append("  % Tetramers 5..8 (Diameter = 10.6 mm, Linear 1x4 Strip)")
    lines.append("  % ==========================================================")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at ({x_left_label:.2f}, {-2.25:.2f}) {{II. Luxury Monograph Model (432 pp, 48/page, $\\varnothing = 10.6\\text{{ mm}}$, linear strip)}};")
    lines.append(f"  \\node[anchor=east, font=\\itshape\\scriptsize, color=black!60] at ({x_right_label:.2f}, {-2.25:.2f}) {{Tetramers $T_5 \\dots T_8$ ($|O|=8$)}};")

    x_start2 = 3.75
    dx2 = 7.50
    # Row 1 of Tier 2: T5, T6
    y2_r1 = -3.70
    for i, idx in enumerate([4, 5]):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start2 + i * dx2
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y2_r1, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r2, d_inner=d_inner2, pad_x=pad_x2, pad_y=pad_y2, font_badge="\\scriptsize"
        ))

    # Row 2 of Tier 2: T7, T8
    y2_r2 = -6.20
    for i, idx in enumerate([6, 7]):
        t_key, t_cycle, t_sz = tetramers[idx]
        cx = x_start2 + i * dx2
        lines.extend(render_linear_cartouche(
            cx=cx, cy=y2_r2, t_num=idx + 1, orb_sz=t_sz, cycle=t_cycle,
            r=r2, d_inner=d_inner2, pad_x=pad_x2, pad_y=pad_y2, font_badge="\\scriptsize"
        ))

    # -------------------------------------------------------------
    # TIER 3: Gold-Tooled Leather-Bound (864-page model, 24 tetramers/page)
    # 4 cartouches in 2 rows of 2: T9..T12
    # r = 0.75 cm (dia = 15.0 mm), d_inner = 1.80 cm, pad_x = 0.85 cm, pad_y = 0.70 cm
    # Box width = 3 * 1.80 + 1.70 = 7.10 cm
    # Pitch dx = 7.50 cm
    # -------------------------------------------------------------
    r3 = 0.75
    d_inner3 = 1.80
    pad_x3 = 0.85
    pad_y3 = 0.70

    lines.append("\n  % ==========================================================")
    lines.append("  % TIER 3: Gold-Tooled Leather-Bound Model (864 Pages, 24 Tetramers / Page)")
    lines.append("  % Tetramers 9..12 (Diameter = 15.0 mm, Linear 1x4 Strip)")
    lines.append("  % ==========================================================")
    lines.append(f"  \\node[anchor=west, font=\\bfseries\\sffamily\\small, color=blue!75!black] at ({x_left_label:.2f}, {-8.45:.2f}) {{III. Gold-Tooled Leather-Bound Model (864 pp, 24/page, $\\varnothing = 15.0\\text{{ mm}}$, linear strip)}};")
    lines.append(f"  \\node[anchor=east, font=\\itshape\\scriptsize, color=black!60] at ({x_right_label:.2f}, {-8.45:.2f}) {{Tetramers $T_9 \\dots T_{12}$ ($|O|=8$)}};")

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
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ Generated linear tetramer comparison plate at {output_path}")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "tkz", "fig_tetramer_scale_comparison.tkz")
    generate_comparison_plate(out)
