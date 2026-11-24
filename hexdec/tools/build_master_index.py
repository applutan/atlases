#!/usr/bin/env python3
"""
build_master_index.py - Assemble the complete master index hexdec/data/hexadecality_index.txt
containing all 21,030 Affine Macro-Orbits:
- 14 Monomers (M01 .. M14)
- 295 Dimers (D001 .. D295)
- 20,721 Tetramers (T00001 .. T20721)

Author: Gemma Knee
"""

import os

def assemble_index():
    index_path = "hexdec/data/hexadecality_index.txt"
    tetramers_path = "hexdec/data/tetramers_full_index.txt"

    with open(index_path, "r") as f:
        lines = f.readlines()

    # Find where Section III (Tetramers) starts
    cut_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("# --- III. TETRAMERS"):
            cut_idx = i
            break

    if cut_idx == -1:
        raise ValueError("Could not find Section III in hexadecality_index.txt")

    header_and_monomers_dimers = lines[:cut_idx]

    # Read tetramers
    with open(tetramers_path, "r") as f:
        tet_lines = f.readlines()

    # Skip comments in tetramers_path
    tet_data = [l for l in tet_lines if not l.startswith("#")]

    out_lines = header_and_monomers_dimers
    out_lines.append("# --- III. TETRAMERS (4-Cycles under mu_3, Complete Census: 20,721 Orbits) ---\n")
    out_lines.extend(tet_data)

    with open(index_path, "w") as f:
        f.writelines(out_lines)

    print(f"✓ Successfully wrote complete master index to {index_path} ({len(out_lines)} lines).")

if __name__ == "__main__":
    assemble_index()
