#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import find_fixed_point_orbits
from hexdec.tools.mosaic_sorting import get_mosaic_sort_key, is_block_symmetric, compute_mosaic_chord_energy

fixed_orbits = find_fixed_point_orbits(16, 4, 4)
monomers = []
for orb in fixed_orbits:
    rep = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
    sz = len(orb)
    key = get_mosaic_sort_key(rep, sz, 16)
    monomers.append((key, rep, sz))

monomers.sort(key=lambda x: x[0])

print("Natural Ordering of the 14 Monomers:")
print(f"{'#':<3} {'Size':<6} {'Sym':<5} {'Energy':<8} {'Canonical Strides':<45} {'Blocks'}")
print("-" * 110)
for idx, (key, rep, sz) in enumerate(monomers, 1):
    s_blocks = sorted([sorted(list(b)) for b in rep])
    sym_cnt = sum(1 for b in s_blocks if is_block_symmetric(b, 16))
    energy = compute_mosaic_chord_energy(s_blocks, 16)
    strides = " + ".join(str(s) for s in key[3])
    print(f"{idx:2d}  {sz:<6} {sym_cnt:<5} {energy:<8} {strides:<45} {s_blocks}")
