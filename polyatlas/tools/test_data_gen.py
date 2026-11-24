#!/usr/bin/env python3
"""test_data_gen.py - Verifies orbit counts and generation speed up to Z_16."""
import time
import math
from generate_poly_atlas_v2 import generate_all_rings_data, count_dihedral_bracelets

t0 = time.time()
print("Starting generation up to Z_16...")
all_rings = generate_all_rings_data(16)
t1 = time.time()
print(f"Generation completed in {t1 - t0:.2f} seconds.")

total_orbits = sum(len(all_rings[n]) for n in range(3, 17))
print(f"Total dihedral orbits generated: {total_orbits}")
for n in range(3, 17):
    print(f"Z_{n:2d}: {len(all_rings[n]):5d} orbits (expected sum = {sum(count_dihedral_bracelets(n, k) for k in range(n+1)):5d})")
