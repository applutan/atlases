#!/usr/bin/env python3
"""
generate_z9_plates.py - Visual Cartographic Plates Generator for Z_9 Mosaics

Reads canonical mosaics from allmosatlas/data/mosaics.tsv for ring n=9
and emits high-density TikZ plates (23 pages, 60 mosaics/page, 1,350 mosaics total).

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import math
import csv
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Generate TikZ visual plates booklet for Z_9 composition mosaics.")
    parser.add_argument(
        "--mosaics-tsv",
        type=str,
        default="/home/paul/gemai/atlases/allmosatlas/data/mosaics.tsv",
        help="Path to mosaics.tsv"
    )
    parser.add_argument(
        "--output-tex",
        type=str,
        default="/home/paul/gemai/atlases/allmosatlas/plates/plates_z9.tex",
        help="Output path for TikZ LaTeX plates file"
    )
    return parser.parse_args()

def load_z9_mosaics(tsv_path):
    mosaics = []
    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["n"] == "9":
                slash = row["slash"].strip("/")
                block_strs = slash.split("/")
                part = [[int(ch, 16) for ch in b] for b in block_strs]
                chirality = row["chirality"]
                block_syms = [ch == "s" for ch in chirality]

                mosaics.append({
                    "n": 9,
                    "id": int(row["id"]),
                    "partition": part,
                    "block_syms": block_syms,
                    "orbit_size": int(row["orbit_size"]),
                    "slash": row["slash"]
                })
    return mosaics

def draw_mosaic_tile(f, o, cx, cy, r=0.62):
    n = 9
    angles = [math.radians(90.0 - k * (360.0 / n)) for k in range(n)]
    cos_v = [math.cos(a) for a in angles]
    sin_v = [math.sin(a) for a in angles]

    wire_pts = [f"({cx + r * cos_v[k]:.3f},{cy + r * sin_v[k]:.3f})" for k in range(n)]
    f.write(f"  \\draw[gray!35, line width=0.25pt] {' -- '.join(wire_pts)} -- cycle;\n")

    for blk, is_sym in zip(o["partition"], o["block_syms"]):
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

    f.write(f"  \\node[anchor=north west, font=\\footnotesize\\bfseries\\sffamily, text=black!85, inner sep=0pt] at ({cx - 1.15:.3f},{cy + 0.90:.3f}) {{{o['id']}}};\n")
    f.write(f"  \\node[anchor=south east, font=\\scriptsize\\sffamily, text=black!55, inner sep=0pt] at ({cx + 1.15:.3f},{cy - 0.90:.3f}) {{{o['orbit_size']}}};\n")

def generate_plates(mosaics, out_tex):
    os.makedirs(os.path.dirname(os.path.abspath(out_tex)), exist_ok=True)
    cols = 6
    rows_per_page = 10
    per_page = cols * rows_per_page  # 60
    pitch_x = 2.90
    pitch_y = 2.45
    r = 0.62

    total_mosaics = len(mosaics)
    total_pages = math.ceil(total_mosaics / per_page)

    with open(out_tex, "w", encoding="utf-8") as f:
        f.write("% Auto-generated visual plates for Z_9 composition mosaics\n")
        f.write("\\documentclass[11pt,a4paper]{article}\n")
        f.write("\\usepackage[margin=1.2cm]{geometry}\n")
        f.write("\\usepackage{amsmath,amssymb}\n")
        f.write("\\usepackage{tikz}\n")
        f.write("\\usepackage{xcolor}\n")
        f.write("\\definecolor{mosaicblue}{RGB}{74, 128, 196}\n")
        f.write("\\definecolor{mosaicpink}{RGB}{224, 102, 102}\n")
        f.write("\\pagestyle{empty}\n")
        f.write("\\begin{document}\n\n")

        for page in range(total_pages):
            start_idx = page * per_page
            end_idx = min(start_idx + per_page, total_mosaics)
            chunk = mosaics[start_idx:end_idx]

            f.write(f"% Plate Page {page + 1} of {total_pages} (Mosaics {start_idx + 1}..{end_idx})\n")
            f.write("\\noindent\\makebox[\\textwidth][c]{\\begin{tikzpicture}[scale=1.0]\n")

            for idx_in_page, o in enumerate(chunk):
                c = idx_in_page % cols
                row = idx_in_page // cols
                cx = c * pitch_x
                cy = - (row * pitch_y)
                draw_mosaic_tile(f, o, cx, cy, r)

            f.write("\\end{tikzpicture}}\\clearpage\n\n")

        f.write("\\end{document}\n")

    print(f"✓ Wrote {total_pages} pages ({total_mosaics} mosaics) to {out_tex}")

def main():
    args = parse_args()
    print("Loading Z_9 mosaics...")
    mosaics = load_z9_mosaics(args.mosaics_tsv)
    print(f"Loaded {len(mosaics)} mosaics for Z_9.")
    generate_plates(mosaics, args.output_tex)

if __name__ == "__main__":
    main()
