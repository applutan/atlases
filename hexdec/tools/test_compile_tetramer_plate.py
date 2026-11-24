#!/usr/bin/env python3
"""
test_compile_tetramer_plate.py - Benchmark compilation of Tetramer atlas pages.

Author: Gemma Knee
"""

import time
import subprocess
import os

# Let's write a test LaTeX file with 1 page, 5 pages, and 10 pages of 96 tetramers
# using the dotless TikZ macro.
def generate_test_tex(n_pages=1, tetramers_per_page=96):
    r = 0.28
    d_inner = 0.65
    pad_x = 0.35
    pad_y = 0.20
    w_half = 1.5 * d_inner + pad_x
    h_half = r + pad_y

    lines = []
    lines.append(r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=1.5cm, top=1.8cm, bottom=1.8cm]{geometry}
\usepackage{tikz}
\usetikzlibrary{calc}
\input{mosaic_tikz_preamble.tex}
\pagestyle{empty}
\begin{document}
""")

    for p in range(n_pages):
        lines.append(r"\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=1.0]")
        # 4 cols x 24 rows
        for row in range(24):
            for col in range(4):
                idx = p * tetramers_per_page + row * 4 + col + 1
                cx = 1.80 + col * 4.45
                cy = -(row * 1.05)
                bx1 = cx - w_half
                bx2 = cx + w_half
                by1 = cy - h_half
                by2 = cy + h_half

                lines.append(f"\\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=3pt, line width=0.35pt] ({bx1:.2f}, {by1:.2f}) rectangle ({bx2:.2f}, {by2:.2f});")
                lines.append(f"\\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=1.5pt, inner sep=1pt, font=\\tiny\\bfseries] at ({bx1 + 0.10:.2f}, {by2:.2f}) {{{idx}}};")
                lines.append(f"\\node[anchor=east, font=\\tiny\\color{{black!50}}] at ({bx2 - 0.10:.2f}, {by1 + 0.10:.2f}) {{32}};")

                # 4 dummy hexagons
                for step in range(4):
                    mx = cx - 1.5 * d_inner + step * d_inner
                    my = cy
                    lines.append(f"\\draw[gray!35, line width=0.2pt] ({mx:.2f},{my:.2f}) circle ({r:.2f});")
                    lines.append(f"\\fill[mosaicblue, fill opacity=0.6] ({mx - r*0.7:.2f},{my - r*0.7:.2f}) rectangle ({mx + r*0.7:.2f},{my + r*0.7:.2f});")

        lines.append(r"\end{tikzpicture}")
        lines.append(r"\newpage")

    lines.append(r"\end{document}")
    return "\n".join(lines)

def run_benchmark():
    for n_pages in [1, 5, 10]:
        tex = generate_test_tex(n_pages)
        test_file = f"hexdec/plates/bench_{n_pages}p.tex"
        with open(test_file, "w") as f:
            f.write(tex)

        t0 = time.time()
        cmd = ["pdflatex", "-interaction=nonstopmode", "-output-directory=plates", f"plates/bench_{n_pages}p.tex"]
        res = subprocess.run(cmd, cwd="hexdec", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        dur = time.time() - t0
        pdf_path = f"hexdec/plates/bench_{n_pages}p.pdf"
        sz_kb = os.path.getsize(pdf_path) / 1024 if os.path.exists(pdf_path) else 0
        print(f"Pages: {n_pages:2d} | Time: {dur:5.2f}s ({dur/n_pages:5.2f}s/page) | Size: {sz_kb:6.1f} KB | Return code: {res.returncode}")

if __name__ == "__main__":
    run_benchmark()
