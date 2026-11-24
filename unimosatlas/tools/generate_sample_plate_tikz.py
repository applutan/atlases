#!/usr/bin/env python3
"""
generate_sample_plate_tikz.py - Generate a prototype TikZ plate showing 8 hexadecagons in a row
demonstrating 4-cycle quartets with directed cycling arrows.
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
    
    # Simple search for partitions
    elements = set(range(n))
    # We construct partitions systematically
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
                
                # Check orbit length under mu_3
                o1 = get_orbit(p)
                p2 = apply_aff(p, 3, 0)
                o2 = get_orbit(p2)
                if o1 == o2:
                    continue
                p3 = apply_aff(p, 7, 0)
                o3 = get_orbit(p3)
                if o3 in (o1, o2):
                    continue
                p4 = apply_aff(p, 5, 0)
                o4 = get_orbit(p4)
                if o4 in (o1, o2, o3):
                    continue
                
                # We have a full quartet of 4 distinct orbits!
                quartets.append([get_canonical_rep(o1), get_canonical_rep(o2), get_canonical_rep(o3), get_canonical_rep(o4)])
                if len(quartets) == 2:
                    return quartets
    return quartets

def generate_plate_tikz(output_path):
    quartets = find_sample_quartets(16, 4, 4)
    assert len(quartets) == 2, "Expected 2 sample quartets"
    
    lines = []
    lines.append("% TikZ prototype plate: 8 hexadecagons in a row demonstrating 2 full 4-cycle quartets")
    lines.append("\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=0.74]")
    lines.append("  \\tikzstyle{hexadecagon}=[regular polygon, regular polygon sides=16, minimum size=1.75cm, draw=gray!40, thin]")
    
    dx = 2.45
    
    # We display 2 quartets side by side in one row (or 2 rows of 4)
    # The user asked: '8 hexadecagons in a row'
    for q_idx, q in enumerate(quartets):
        for step in range(4):
            idx = q_idx * 4 + step
            cx = idx * dx + (0.5 if q_idx == 1 else 0.0) # small extra gap between the two quartets
            cy = 0.0
            p = q[step]
            blocks = sorted([sorted(list(b)) for b in p])
            
            lines.append(f"  % Quartet {q_idx+1}, Step {step+1} (x = {cx:.2f})")
            lines.append(f"  \\begin{{scope}}[shift={{({cx:.2f}, {cy:.2f})}}]")
            lines.append(f"    \\node[hexadecagon] (H{idx}) at (0,0) {{}};")
            
            for b in blocks:
                sym = is_block_symmetric(b, 16)
                col_name = "mosaicblue" if sym else "mosaicpink"
                corners = " -- ".join(f"(H{idx}.corner {x+1})" for x in b)
                lines.append(f"    \\fill[{col_name}, fill opacity=0.60] {corners} -- cycle;")
                lines.append(f"    \\draw[black!85, line width=0.45pt] {corners} -- cycle;")
                
            labels = ["O", "\\mu_3(O)", "\\mu_7(O)", "\\mu_5(O)"]
            lines.append(f"    \\node[below=0.92cm of H{idx}.center, inner sep=0.5pt] {{\\scriptsize ${labels[step]}^{{({q_idx+1})}}$}};")
            lines.append(f"  \\end{{scope}}")
            
        # Draw forward transition arrows between consecutive members of the quartet
        for step in range(3):
            idx1 = q_idx * 4 + step
            idx2 = idx1 + 1
            lines.append(f"  \\draw[->, blue!75!black, line width=0.8pt] (H{idx1}.east) -- (H{idx2}.west) node[midway, above=-1pt] {{\\tiny $\\mu_3$}};")
            
        # Draw loop-back curved arrow from step 3 (H3) back to step 0 (H0)
        idx0 = q_idx * 4
        idx3 = q_idx * 4 + 3
        lines.append(f"  \\draw[->, blue!75!black, dashed, line width=0.7pt] (H{idx3}.north) to[bend right=25] node[midway, above=-1pt] {{\\tiny $\\mu_3$}} (H{idx0}.north);")
        
    lines.append("\\end{tikzpicture}")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ Generated {output_path} with 8 hexadecagons in a row.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate prototype TikZ plate showing 8 hexadecagons in a row with cycling arrows.")
    default_out = os.path.join(os.path.dirname(__file__), "..", "tkz", "fig_sample_plate.tkz")
    parser.add_argument("-o", "--out", type=str, default=default_out, help=f"Output path (default: {default_out})")
    args = parser.parse_args()
    generate_plate_tikz(args.out)
