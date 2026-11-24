#!/usr/bin/env python3
"""
check_quartet_orbit_sizes.py - Check the dihedral orbit size distribution among the 20,721 Quartets
"""

import sys
import os
from collections import defaultdict

# Total D_16 orbits = 83488
# Monomers: 1*1 + 3*4 + 4*16 + 6*32 = 1 + 12 + 64 + 192 = 269 D_16 orbits
# Doublets: 1*2 + 1*4 + 9*8 + 38*16 + 246*32 = 2 + 4 + 72 + 608 + 7872 = 8558 D_16 orbits
# Quartets: 83488 - 269 - 8558 = 74661 D_16 orbits!
# Wait! Let's check this calculation:
# Earlier affine_macro_orbits.py output:
#   Monomers (Size 1): 14 macro-orbits, 14 D_16 orbits!
#   Wait! A monomer is ONE D_16 orbit!
#   14 monomers = 14 D_16 orbits!
#   295 doublets = 295 * 2 = 590 D_16 orbits!
#   20721 quartets = 20721 * 4 = 82884 D_16 orbits!
#   14 + 590 + 82884 = 83488 D_16 orbits!

print("Total D_16 orbits: 83,488")
print("  In Monomers (14 macro-orbits):    14 D_16 orbits")
print("  In Doublets (295 macro-orbits):  590 D_16 orbits")
print("  In Quartets (20721 macro-orbits): 82884 D_16 orbits")

# What are the dihedral orbit sizes of those 82,884 D_16 orbits?
# Let's check how many total D_16 orbits of each size exist in Z_16, z_4^4!
