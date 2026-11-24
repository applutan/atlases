#!/usr/bin/env python3
"""
generate_multilattice_relational_data.py - Relational Mosaic-Composition Bridge for Z_1..Z_8

Bridges all 509 dihedral composition mosaics across rings Z_1 through Z_8
to the individual inscribed polygon orbits of polyatlas (inngons.tsv).

Outputs:
1. octatlas/data/mosaics.tsv, mosaics.csv, mosaics.json
   Consolidated mosaic-level catalogue (509 records) featuring:
   - Global ID (1..509), Ring n (1..8), Local ID (1..M_n)
   - Dihedral invariants: |O|, |Stab|, s_count, chirality [ssss]
   - Circular chord energy E
   - poly_profile: Multi-set of constituent polyatlas classes (e.g. 2-1+2-1)
   - block_manifest: Concise embedding descriptor (e.g. 2-1@0+:13/2-1@2+:13)
2. octatlas/data/mosaic_blocks.tsv, mosaic_blocks.csv, mosaic_blocks.json
   Block-level relational table (all constituent blocks across all 509 mosaics) featuring:
   - global_mosaic_id, n, local_mosaic_id, block_idx
   - block vertices on Z_n
   - polyatlas class_id (e.g. 3-1) and canonical stride composition
   - realised cyclic stride composition
   - spatial root vertex min(B)
   - chirality orientation: + (direct) vs - (retrograde / flipped)

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import json
import csv
import argparse
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Set

from generate_multilattice_atlas import (
    compute_ring_mosaics,
    get_dihedral_ops,
    is_block_symmetric,
    compute_block_energy,
    canonicalise_partition,
    format_slash
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate relational TSV/CSV/JSON datasets bridging Z_1..Z_8 mosaics to polyatlas compositions."
    )
    parser.add_argument(
        "--inngons-tsv",
        type=str,
        default="/home/paul/gemai/atlases/polyatlas/data/inngons.tsv",
        help="Path to polyatlas inngons.tsv"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="octatlas/data",
        help="Output directory for relational datasets"
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=8,
        help="Maximum ring order (default: 8)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        default=True,
        help="Run integrity verification on all generated manifests"
    )
    return parser.parse_args()

def load_polyatlas_all(inngons_path: str, max_n: int = 8) -> Dict[Tuple[int, Tuple[int, ...]], Dict[str, Any]]:
    """Load canonical polygon orbits from polyatlas keyed by (n, canonical_tuple)."""
    if not os.path.exists(inngons_path):
        raise FileNotFoundError(f"Cannot find inngons.tsv at {inngons_path}")

    poly_map = {}
    with open(inngons_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        for parts in reader:
            if len(parts) < 7:
                continue
            comp, class_id, n_str, k_str, subset_slash, orb_sz, is_achiral = parts[:7]
            if not n_str.isdigit():
                continue
            n = int(n_str)
            if n > max_n or n < 1:
                continue
            k = int(k_str)
            if k == 0:
                continue  # skip empty set

            clean_slash = subset_slash.strip("/")
            if clean_slash == "":
                subset_tuple = ()
            else:
                subset_tuple = tuple(int(ch, 16) for ch in clean_slash)

            poly_map[(n, subset_tuple)] = {
                "n": n,
                "class_id": class_id,
                "composition": comp,
                "k": k,
                "is_achiral": bool(int(is_achiral)),
                "orbit_size": int(orb_sz),
                "subset_slash": subset_slash
            }
    return poly_map

def canonicalise_subset(subset: List[int], n: int) -> Tuple[int, ...]:
    """Find canonical subset under D_n."""
    if not subset:
        return ()
    ops = get_dihedral_ops(n)
    best = None
    for a, b in ops:
        cand = tuple(sorted((a * x + b) % n for x in subset))
        if best is None or cand < best:
            best = cand
    return best

def get_block_strides(block: List[int], n: int) -> str:
    """Return forward cyclic strides around block perimeter."""
    m = len(block)
    if m <= 1:
        return str(n)
    sb = sorted(block)
    strides = [(sb[(i + 1) % m] - sb[i]) % n for i in range(m)]
    return "".join(f"{s:X}" for s in strides)

def analyze_block_embedding(block: List[int], n: int, poly_map: Dict[Tuple[int, Tuple[int, ...]], Dict[str, Any]]):
    """
    Relates block B to its canonical parent polygon in polyatlas for ring n.
    """
    sb = sorted(block)
    canon_sub = canonicalise_subset(sb, n)
    p_info = poly_map.get((n, canon_sub))
    if not p_info:
        raise KeyError(f"Canonical subset {canon_sub} on Z_{n} not found in polyatlas data")

    poly_class = p_info["class_id"]
    canon_comp = p_info["composition"]
    is_achiral = p_info["is_achiral"]
    realised_comp = get_block_strides(sb, n)
    root = sb[0]

    # Chirality orientation: + for direct cyclic translation, - for retrograde / flipped
    direct_match = False
    for b in range(n):
        trans = tuple(sorted((x + b) % n for x in canon_sub))
        if trans == tuple(sb):
            direct_match = True
            break

    if is_achiral:
        chirality_char = "+"
    else:
        chirality_char = "+" if direct_match else "-"

    token = f"{poly_class}@{root}{chirality_char}:{realised_comp}"
    return {
        "poly_class": poly_class,
        "canon_comp": canon_comp,
        "realised_comp": realised_comp,
        "root": root,
        "chirality": chirality_char,
        "manifest_token": token
    }

def main():
    args = parse_args()
    print("=" * 80)
    print("OCTATLAS MULTI-LATTICE RELATIONAL BRIDGE: MOSAICS <-> COMPOSITIONS")
    print("=" * 80)

    # 1. Load polyatlas data
    print(f"Loading polyatlas reference from: {args.inngons_tsv}")
    poly_map = load_polyatlas_all(args.inngons_tsv, args.max_n)
    print(f"✓ Loaded {len(poly_map)} polygon orbits across Z_1..Z_{args.max_n} from polyatlas.")

    # 2. Compute mosaics for all rings
    all_mosaic_rows = []
    all_block_rows = []
    global_id_counter = 1

    for n in range(1, args.max_n + 1):
        print(f"Analyzing ring Z_{n}...")
        rd = compute_ring_mosaics(n)

        for o in rd['orbits']:
            m_id = global_id_counter
            o['global_id'] = m_id
            global_id_counter += 1

            part = o['partition']
            block_tokens = []
            poly_classes = []

            for b_idx, blk in enumerate(part, 1):
                emb = analyze_block_embedding(blk, n, poly_map)
                block_tokens.append(emb["manifest_token"])
                poly_classes.append(emb["poly_class"])

                all_block_rows.append({
                    "n": n,
                    "mosaic_id": o['local_id'],
                    "block_idx": b_idx,
                    "vertices": "".join(f"{x:X}" for x in blk),
                    "size": len(blk),
                    "poly_class": emb["poly_class"],
                    "canon_comp": emb["canon_comp"],
                    "realised_comp": emb["realised_comp"],
                    "root": emb["root"],
                    "chirality": emb["chirality"]
                })

            manifest = "/".join(block_tokens)
            poly_profile = "+".join(sorted(poly_classes))
            shape_str = "(" + ",".join(str(x) for x in o['shape']) + ")"

            all_mosaic_rows.append({
                "n": n,
                "id": o['local_id'],
                "shape": shape_str,
                "slash": o['slash'],
                "orbit_size": o['orbit_size'],
                "stab_size": o['stab_size'],
                "s_count": o['s_count'],
                "chirality": o['sig'],
                "energy": o['energy'],
                "poly_profile": poly_profile,
                "manifest": manifest
            })

    total_mosaics = len(all_mosaic_rows)
    total_blocks = len(all_block_rows)
    print("-" * 80)
    print(f"Extracted {total_mosaics} mosaics and {total_blocks} relational blocks across Z_1..Z_{args.max_n}.")
    print("-" * 80)

    # 3. Write datasets (TSV, CSV, JSON) - strictly NO leading comments in TSV/CSV
    os.makedirs(args.data_dir, exist_ok=True)

    mosaic_tsv_path = os.path.join(args.data_dir, "mosaics.tsv")
    mosaic_csv_path = os.path.join(args.data_dir, "mosaics.csv")
    mosaic_json_path = os.path.join(args.data_dir, "mosaics.json")

    block_tsv_path = os.path.join(args.data_dir, "mosaic_blocks.tsv")
    block_csv_path = os.path.join(args.data_dir, "mosaic_blocks.csv")
    block_json_path = os.path.join(args.data_dir, "mosaic_blocks.json")

    mosaic_fieldnames = ["n", "id", "shape", "slash", "orbit_size", "stab_size", "s_count", "chirality", "energy", "poly_profile", "manifest"]
    block_fieldnames = ["n", "mosaic_id", "block_idx", "vertices", "size", "poly_class", "canon_comp", "realised_comp", "root", "chirality"]

    # Mosaics TSV
    with open(mosaic_tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=mosaic_fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_mosaic_rows)
    print(f"✓ Wrote {total_mosaics} mosaic records: {mosaic_tsv_path}")

    # Mosaics CSV
    with open(mosaic_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=mosaic_fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_mosaic_rows)
    print(f"✓ Wrote {total_mosaics} mosaic records: {mosaic_csv_path}")

    # Mosaics JSON
    with open(mosaic_json_path, "w", encoding="utf-8") as f:
        json.dump(all_mosaic_rows, f, indent=2)
    print(f"✓ Wrote {total_mosaics} mosaic records: {mosaic_json_path}")

    # Blocks TSV
    with open(block_tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=block_fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_block_rows)
    print(f"✓ Wrote {total_blocks} block records: {block_tsv_path}")

    # Blocks CSV
    with open(block_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=block_fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_block_rows)
    print(f"✓ Wrote {total_blocks} block records: {block_csv_path}")

    # Blocks JSON
    with open(block_json_path, "w", encoding="utf-8") as f:
        json.dump(all_block_rows, f, indent=2)
    print(f"✓ Wrote {total_blocks} block records: {block_json_path}")

    # 4. Verification of invertibility
    if args.verify:
        print("\nVerifying manifest invertibility across all 509 mosaics...")
        for r in all_mosaic_rows:
            n = r['n']
            manifest = r['manifest']
            expected_slash = r['slash']
            tokens = manifest.split("/")
            reconstructed_blocks = []
            for tok in tokens:
                root_part, strides_part = tok.split(":")
                root = int(root_part.split("@")[1][:-1])
                verts = [root]
                curr = root
                if n > 1 and len(strides_part) > 1:
                    for s_ch in strides_part[:-1]:
                        s = int(s_ch, 16)
                        curr = (curr + s) % n
                        verts.append(curr)
                reconstructed_blocks.append(sorted(verts))
            recon_slash = format_slash(reconstructed_blocks)
            assert recon_slash == expected_slash, f"Mismatch on mosaic {r['id']} (Z_{n}): {recon_slash} != {expected_slash}"
        print("✓ All 509 manifests verified: 100% bijective and reversible!")

if __name__ == "__main__":
    main()
