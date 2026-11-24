#!/usr/bin/env python3
"""
generate_monomer_tikz.py - Generate TikZ figures for the 14 Monomer Mosaics of z_4^4 on Z_16

Arranged in 2 rows of 7 mosaics, strictly sorted by the 5-tier natural geometric cascade:
1. Dihedral orbit size |O|
2. Symmetric block count s (descending)
3. Chord dispersion energy E (descending)
4. Canonical stride profile multiset
5. Canonical lexicographical tie-breaker
"""

import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import find_fixed_point_orbits
from hexdec.tools.mosaic_sorting import get_mosaic_sort_key, is_block_symmetric

def get_hexadecagon_coords(r=0.875):
    coords = []
    for k in range(16):
        ang = math.radians(90.0 - k * 22.5)
        coords.append((r * math.cos(ang), r * math.sin(ang)))
    return coords

def generate_monomers_tikz(output_path):
    fixed_orbits = find_fixed_point_orbits(16, 4, 4)
    monomers = []
    for orb in fixed_orbits:
        rep = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        sz = len(orb)
        key = get_mosaic_sort_key(rep, sz, 16)
        monomers.append((key, rep, sz))
    
    # Sort strictly by the 5-tier cascade
    monomers.sort(key=lambda x: x[0])
    
    r = 0.875
    unit_coords = get_hexadecagon_coords(r)
    wire_path = " -- ".join(f"({x:.3f},{y:.3f})" for x, y in unit_coords) + " -- cycle"

    lines = []
    lines.append("% TikZ code for the 14 Monomer Mosaics of z_4^4 on Z_16")
    lines.append("% Strictly ordered by the 5-tier natural geometric cascade")
    lines.append("% Arranged in 2 rows of 7 mosaics")
    lines.append("% Oriented consistently with polyatlas (vertex 0 at zenith, clockwise)")
    lines.append("\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=0.78]")
    
    # We display them in 2 rows of 7 mosaics: col 0..6, row 0..1
    dx = 2.45
    dy = 2.80
    
    for idx, (key, rep, orb_sz) in enumerate(monomers):
        col = idx % 7
        row = idx // 7
        cx = col * dx
        cy = -row * dy
        
        blocks = sorted([sorted(list(b)) for b in rep])
        
        lines.append(f"  % Monomer #{idx+1} (D_16 orbit size {orb_sz}, sym={-key[1]}, energy={-key[2]})")
        lines.append(f"  \\begin{{scope}}[shift={{({cx:.2f}, {cy:.2f})}}]")
        lines.append(f"    \\draw[gray!40, line width=0.35pt] {wire_path};")
        
        for b in blocks:
            s_blk = sorted(list(b))
            sym = is_block_symmetric(s_blk, 16)
            col_name = "mosaicblue" if sym else "mosaicpink"
            corners = " -- ".join(f"({unit_coords[x][0]:.3f},{unit_coords[x][1]:.3f})" for x in s_blk) + " -- cycle"
            lines.append(f"    \\fill[{col_name}, fill opacity=0.60] {corners};")
            lines.append(f"    \\draw[black!85, line width=0.45pt] {corners};")

        for vx, vy in unit_coords:
            lines.append(f"    \\fill[black!80] ({vx:.3f},{vy:.3f}) circle (0.5pt);")

        # Distinguishing value: orbit size
        lines.append(f"    \\node[below={r + 0.16:.2f}cm, inner sep=0.5pt, font=\\scriptsize] {{{orb_sz}}};")
        lines.append(f"  \\end{{scope}}")
        
    lines.append("\\end{tikzpicture}")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ Generated {output_path} with {len(monomers)} sorted monomers.")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "tkz", "fig_14_monomers.tkz")
    generate_monomers_tikz(out)
