#!/usr/bin/env python3
"""
check_all_orbit_sizes.py - Check the distribution of D_16 orbit sizes across all 83,488 orbits
and see how they partition into Monomers, Doublets, and Quartets.
"""

import sys
import os
import sqlite3
from collections import defaultdict

# Let's inspect the database if available, or compute orbit size counts via Burnside
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import get_affine_group, find_fixed_point_orbits, get_units

def check_stabilizer_orders():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".cache", "mosaics_cache.db"))
    if not os.path.exists(db_path):
        print("Database not found at", db_path)
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check shapes present in database
    shapes = cur.execute("SELECT DISTINCT n, shape, grp FROM canonical_mosaics").fetchall()
    print("Shapes present in db:", shapes)
    
    # Check if z_4^4 is present
    res = cur.execute("SELECT orbit_size, COUNT(*) FROM canonical_mosaics WHERE n=16 GROUP BY orbit_size").fetchall()
    print("Z_16 orbit sizes in db:", res)
    conn.close()

if __name__ == "__main__":
    check_stabilizer_orders()
