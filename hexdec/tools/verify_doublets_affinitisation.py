#!/usr/bin/env python3
import json

with open("hexdec/data/doublets.json") as f:
    data = json.load(f)

print(f"Checking all {len(data)} doublets:")
errors = 0
for idx, d in enumerate(data):
    p1 = [sorted(b) for b in d["p1"]]
    p2 = [sorted(b) for b in d["p2"]]
    
    # Check if elements of p1 and p2 are valid partitions of Z_16
    all1 = sorted([x for b in p1 for x in b])
    all2 = sorted([x for b in p2 for x in b])
    if all1 != list(range(16)):
        print(f"Doublet #{idx+1} p1 is NOT a partition of Z_16! {all1}")
        errors += 1
    if all2 != list(range(16)):
        print(f"Doublet #{idx+1} p2 is NOT a partition of Z_16! {all2}")
        errors += 1
        
    # Check what mu_3(p1) is
    mu3_p1 = sorted([sorted([(3 * x) % 16 for x in b]) for b in p1])
    
    # Is p2 in the D_16 orbit of mu3_p1?
    d16_elements = [(a, b) for a in [1, 15] for b in range(16)]
    found = False
    for a, b in d16_elements:
        d_p2 = sorted([sorted([(a * x + b) % 16 for x in blk]) for blk in p2])
        if d_p2 == mu3_p1:
            found = True
            break
            
    if not found:
        print(f"Doublet #{idx+1}: p2 is NOT in the D_16 orbit of mu_3(p1)!")
        errors += 1
        
if errors == 0:
    print("All 295 doublets are 100% valid partitions of Z_16 and p2 is confirmed in Orb_D(mu_3(p1))!")
else:
    print(f"Total errors: {errors}")
