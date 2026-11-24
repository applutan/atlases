#!/usr/bin/env python3
"""
generate_doublets_plates.py - Generate TikZ plates for the 295 Doublets of z_4^4 on Z_16

Arranges the 295 doublets in vertical bi-cartouches (top mosaic = O_a, bottom mosaic = O_b).
Default layout:
  5 columns x 5 rows = 25 doublets per page (12 pages: 11 pages of 25, 1 page of 20).
  Because 295 = 5 * 59, EVERY row on EVERY page has exactly 5 doublets.

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

def is_block_symmetric(block, n=16):
    """Check if block is symmetric under reflection in Z_n."""
    sb = sorted(list(block))
    for c in range(n):
        ref_b = sorted([(-x + c) % n for x in sb])
        if ref_b == sb:
            return True
    return False

def get_hexadecagon_vertex_coords(cx: float, cy: float, r: float) -> List[Tuple[float, float]]:
    """Return the 16 (x, y) coordinates of regular hexadecagon with vertex 0 at 90 deg."""
    coords = []
    for k in range(16):
        angle = math.radians(90.0 - k * 22.5)
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return coords

def load_or_extract_doublets(cache_file: str) -> list:
    """Load doublets from JSON cache or compute and save them."""
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            data = json.load(f)
            doublets = []
            for item in data:
                p1 = [sorted(list(b)) for b in item["p1"]]
                p2 = [sorted(list(b)) for b in item["p2"]]
                sz1 = item["sz1"]
                sz2 = item["sz2"]
                doublets.append((p1, p2, sz1, sz2))
            return doublets
            
    print("Extracting doublets from group action...")
    raw_doublets = extract_all_doublets(16, 4, 4)
    
    # Save to JSON as sorted lists
    json_data = []
    doublets = []
    for p1, p2, sz1, sz2 in raw_doublets:
        s_p1 = [sorted(list(b)) for b in p1]
        s_p2 = [sorted(list(b)) for b in p2]
        json_data.append({
            "p1": s_p1,
            "p2": s_p2,
            "sz1": sz1,
            "sz2": sz2
        })
        doublets.append((s_p1, s_p2, sz1, sz2))
    os.makedirs(os.path.dirname(os.path.abspath(cache_file)), exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(json_data, f)
    print(f"Cached {len(json_data)} doublets to {cache_file}")
    return doublets

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
        
    # Draw vertex points
    for x, y in coords:
        lines.append(f"    \\fill[black!85] ({x:.2f},{y:.2f}) circle (0.50pt);")
        
    return lines

def generate_page_tikz(doublets_slice: list, start_idx: int, cols: int = 5,
                       r: float = 0.78, dx: float = 3.48, dy_row: float = 4.60,
                       scale: float = 0.95) -> str:
    """
    Generate TikZ code for a single plate of vertical bi-cartouches.
    """
    lines = []
    lines.append(f"% TikZ Plate: Doublets {start_idx} to {start_idx + len(doublets_slice) - 1}")
    lines.append(f"\\begin{{tikzpicture}}[>=latex, line join=round, line cap=round, scale={scale:.2f}]")
    
    # Vertical bi-cartouche dimensions
    # Distance between top and bottom hexadecagon centers
    dy_inner = 1.85
    # Cartouche bounding box relative to its center (cx, cy)
    pad_x = 1.25
    pad_y = 1.05
    w_half = pad_x
    h_top = dy_inner / 2.0 + pad_y
    h_bot = -dy_inner / 2.0 - pad_y
    
    for idx, (p1, p2, sz1, sz2) in enumerate(doublets_slice):
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
        
        lines.append(f"\n  % --- Bi-Cartouche #{d_num} (Orbit size {sz1}) ---")
        # Soft rounded cartouche box
        lines.append(f"  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=6pt, line width=0.50pt] ({bx1:.2f}, {by1:.2f}) rectangle ({bx2:.2f}, {by2:.2f});")
        
        # Top-left badge: doublet integer
        lines.append(f"  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=2.5pt, inner sep=1.8pt, font=\\scriptsize\\bfseries\\sffamily] at ({bx1 + 0.18:.2f}, {by2:.2f}) {{{d_num}}};")
        
        # Bottom-right badge: orbit size
        lines.append(f"  \\node[anchor=east, font=\\tiny\\color{{black!55}}] at ({bx2 - 0.20:.2f}, {by1 + 0.22:.2f}) {{{sz1}}};")
        
        # Top mosaic: O_a
        top_cy = cy + dy_inner / 2.0
        lines.extend(render_mosaic_tikz(cx, top_cy, r, p1))
        
        # Bottom mosaic: O_b
        bot_cy = cy - dy_inner / 2.0
        lines.extend(render_mosaic_tikz(cx, bot_cy, r, p2))
        
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate TikZ plates for the 295 Doublets.")
    parser.add_argument("--cols", type=int, default=5, help="Columns per page (default: 5)")
    parser.add_argument("--rows", type=int, default=5, help="Rows per page (default: 5)")
    parser.add_argument("--outdir", default="hexdec/tkz/doublets", help="Output directory for TikZ files")
    parser.add_argument("--scale", type=float, default=0.95, help="TikZ scale (default: 0.95)")
    args = parser.parse_args()
    
    cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "doublets.json")
    doublets = load_or_extract_doublets(cache_path)
    
    per_page = args.cols * args.rows
    total_pages = math.ceil(len(doublets) / per_page)
    
    print(f"Generating TikZ plates for {len(doublets)} doublets:")
    print(f"  Layout: {args.cols} cols x {args.rows} rows = {per_page} per page")
    print(f"  Total pages: {total_pages}")
    print(f"  Output directory: {args.outdir}")
    
    os.makedirs(args.outdir, exist_ok=True)
    
    # Also generate a master tex file that includes all plates
    plate_tex_lines = []
    plate_tex_lines.append("% Master inclusion file for all Doublet plates")
    plate_tex_lines.append("\\section{The Complete Catalogue of 295 Doublets}")
    plate_tex_lines.append("\\label{sec:doublets-catalogue}")
    plate_tex_lines.append("")
    plate_tex_lines.append("Each vertical bi-cartouche contains an affine doublet $\\{O_a, O_b\\}$ of shape $z_4^4$ on $\\mathbb{Z}_{16}$, paired under the Galois multiplier $\\mu_3 \\colon x \\mapsto 3x$ (top to bottom). The top-left badge identifies the doublet index ($1, \\dots, 295$); the small bottom-right numeral notes the shared dihedral orbit size $|O| \\in \\{2, 4, 8, 16, 32\\}$.")
    plate_tex_lines.append("")
    
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * per_page + 1
        end_idx = min(page_num * per_page, len(doublets))
        doublets_slice = doublets[(start_idx - 1):end_idx]
        
        filename = f"plate_doublets_{page_num:02d}.tkz"
        filepath = os.path.join(args.outdir, filename)
        
        tikz_content = generate_page_tikz(
            doublets_slice=doublets_slice,
            start_idx=start_idx,
            cols=args.cols,
            scale=args.scale
        )
        
        with open(filepath, "w") as f:
            f.write(tikz_content)
            
        print(f"  [Page {page_num:2d}/{total_pages:2d}] Doublets {start_idx:3d}..{end_idx:3d} ({len(doublets_slice):2d} bi-cartouches) -> {filename}")
        
        plate_tex_lines.append("\\begin{figure}[p]")
        plate_tex_lines.append("\\centering")
        plate_tex_lines.append(f"\\input{{tkz/doublets/{filename}}}")
        plate_tex_lines.append(f"\\caption{{Doublets {start_idx} to {end_idx}}}")
        plate_tex_lines.append("\\end{figure}")
        plate_tex_lines.append("\\clearpage")
        plate_tex_lines.append("")
        
    master_path = os.path.join(os.path.dirname(__file__), "..", "sec", "DoubletsCatalogue.tex")
    with open(master_path, "w") as f:
        f.write("\n".join(plate_tex_lines))
    print(f"✓ Master catalogue file written to {master_path}")

if __name__ == "__main__":
    main()
