#!/usr/bin/env python3
"""
generate_cartouche_sample.py - Generate prototype TikZ plate of two cartouched 4-cycle quartets
"""

import sys
import os
import itertools

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import get_affine_group, analyze_macro_group

def is_block_symmetric(block, n=16):
    sb = sorted(list(block))
    for c in range(n):
        ref_b = sorted([(-x + c) % n for x in sb])
        if ref_b == sb:
            return True
    return False

def get_canonical_rep(orb, n=16):
    sorted_p = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))
    return sorted_p[0]

def find_sample_quartets(n=16, k=4, s=4):
    d_n_elements = [(a, b) for a in [1, n - 1] for b in range(n)]
    
    def apply_aff(p, a, b):
        return frozenset(frozenset((a * x + b) % n for x in blk) for blk in p)

    def get_orbit(p):
        orb = set()
        for a, b in d_n_elements:
            orb.add(apply_aff(p, a, b))
        return orb

    quartets = []
    elements = set(range(n))
    for b1_rest in itertools.combinations(range(1, n), s - 1):
        b1 = frozenset([0] + list(b1_rest))
        rem1 = elements - b1
        min1 = min(rem1)
        rem1_list = sorted(list(rem1 - {min1}))
        for b2_rest in itertools.combinations(rem1_list, s - 1):
            b2 = frozenset([min1] + list(b2_rest))
            rem2 = rem1 - b2
            min2 = min(rem2)
            rem2_list = sorted(list(rem2 - {min2}))
            for b3_rest in itertools.combinations(rem2_list, s - 1):
                b3 = frozenset([min2] + list(b3_rest))
                b4 = frozenset(rem2 - b3)
                p = frozenset([b1, b2, b3, b4])
                
                o1 = get_orbit(p)
                p2 = apply_aff(p, 3, 0)
                o2 = get_orbit(p2)
                if o1 == o2: continue
                p3 = apply_aff(p, 7, 0)
                o3 = get_orbit(p3)
                if o3 in (o1, o2): continue
                p4 = apply_aff(p, 5, 0)
                o4 = get_orbit(p4)
                if o4 in (o1, o2, o3): continue
                
                quartets.append([get_canonical_rep(o1), get_canonical_rep(o2), get_canonical_rep(o3), get_canonical_rep(o4)])
                if len(quartets) == 2:
                    return quartets
    return quartets

def generate_cartouche_tikz(output_path):
    quartets = find_sample_quartets(16, 4, 4)
    
    lines = []
    lines.append("% TikZ prototype plate: Two cartouched 4-cycle quartets side by side")
    lines.append("% Pure minimalist coffee-table presentation: clean numbering, no label noise")
    lines.append("\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=0.83]")
    lines.append("  \\tikzstyle{hexadecagon}=[regular polygon, regular polygon sides=16, minimum size=1.65cm, draw=gray!45, thin]")
    
    # Cartouche layout parameters
    # dx = distance between hexadecagon centers within a cartouche
    dx = 2.25
    # Cartouche margins around the hexadecagons
    pad_x = 1.10
    cartouche_w = 3 * dx + 2 * pad_x  # 3 * 2.25 + 2.20 = 8.95cm
    cartouche_gap = 0.85
    
    for q_idx, q in enumerate(quartets):
        origin_x = q_idx * (cartouche_w + cartouche_gap)
        
        lines.append(f"\n  % --- Cartouche {q_idx+1} ---")
        x_min = origin_x - pad_x
        x_max = origin_x + 3 * dx + pad_x
        
        # Soft, elegant rounded cartouche box
        lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=7pt, line width=0.55pt] ({x_min:.2f}, -1.15) rectangle ({x_max:.2f}, 1.15);")
        # Minimalist number label: simply the quartet integer
        lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=3pt, inner sep=2.5pt, font=\\small\\bfseries\\sffamily] at ({x_min + 0.25:.2f}, 1.15) {{{q_idx+1}}};")
        
        for step in range(4):
            cx = origin_x + step * dx
            cy = 0.0
            idx = q_idx * 4 + step
            p = q[step]
            blocks = sorted([sorted(list(b)) for b in p])
            
            lines.append(f"  \\begin{{scope}}[shift={{({cx:.2f}, {cy:.2f})}}]")
            lines.append(f"    \\node[hexadecagon] (H{idx}) at (0,0) {{}};")
            
            for b in blocks:
                sym = is_block_symmetric(b, 16)
                col_name = "mosaicblue" if sym else "mosaicpink"
                corners = " -- ".join(f"(H{idx}.corner {x+1})" for x in b)
                lines.append(f"    \\fill[{col_name}, fill opacity=0.62] {corners} -- cycle;")
                lines.append(f"    \\draw[black!85, line width=0.45pt] {corners} -- cycle;")
                
            lines.append(f"  \\end{{scope}}")
            
    lines.append("\\end{tikzpicture}")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ Generated clean cartouche sample at {output_path}")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "tkz", "fig_cartouche_sample.tkz")
    generate_cartouche_tikz(out)
