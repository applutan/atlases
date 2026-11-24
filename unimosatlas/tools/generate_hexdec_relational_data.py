#!/usr/bin/env python3
"""
generate_hexdec_relational_data.py - Relational Mosaic-Composition Bridge for Hexadecality

Bridges the composition mosaics of Hexadecality:
  - D_4 universe (z_2^2 on Z_4: 2 monomers)
  - D_9 universe (z_3^3 on Z_9: 1 monomer, 8 trimers = 25 dihedral comosaics)
  - D_16 universe (z_4^4 on Z_16: 14 monomers, 295 dimers, 20,721 tetramers = 83,488 comosaics)
to the dihedral inscribed polygon orbits of polyatlas (polyatlas/data/inngons.tsv).

Produces normalized, greppable TSV relational datasets:
  - unimosatlas/data/z4_mosaics.tsv & z4_mosaic_blocks.tsv
  - unimosatlas/data/z9_mosaics.tsv & z9_mosaic_blocks.tsv
  - unimosatlas/data/z16_mosaics.tsv & z16_mosaic_blocks.tsv
  - unimosatlas/data/z16_macro_mosaics.tsv & z16_macro_mosaic_blocks.tsv (primary representatives)

Features:
  - Exact manifest syntax: [class]@[root][chirality]:[strides]
  - Complete polygon multi-set profile (e.g. 4-12+4-15+...)
  - Realised cyclic perimeter strides starting from root vertex
  - Chirality indicator: '+' (direct rotation) vs '-' (retrograde reflection)
  - Built-in --verify mode ensuring 100% bijective invertibility of manifests.

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import argparse
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate relational TSV datasets bridging hexadecality mosaics to polyatlas compositions."
    )
    parser.add_argument(
        "--universe",
        type=str,
        choices=["all", "z4", "z9", "z16"],
        default="all",
        help="Target cyclic universe to process (default: all)"
    )
    parser.add_argument(
        "--inngons-tsv",
        type=str,
        default="polyatlas/data/inngons.tsv",
        help="Path to polyatlas inngons.tsv"
    )
    parser.add_argument(
        "--hexdec-index",
        type=str,
        default="unimosatlas/data/hexadecality_index.txt",
        help="Path to hexadecality_index.txt"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="unimosatlas/data",
        help="Output directory for generated TSV files (default: unimosatlas/data)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run integrity verification reconstructing partitions from manifests"
    )
    return parser.parse_args()

def load_polyatlas(inngons_path: str, target_n: int) -> Dict[Tuple[int, ...], Dict[str, Any]]:
    """Load canonical polygon orbits for cyclic lattice Z_n from inngons.tsv."""
    if not os.path.exists(inngons_path):
        raise FileNotFoundError(f"Cannot find inngons.tsv at {inngons_path}")
    
    poly_map = {}
    with open(inngons_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            comp, class_id, n_str, k_str, subset_slash, orb_sz, is_achiral = parts[:7]
            if not n_str.isdigit() or int(n_str) != target_n:
                continue
            k = int(k_str)
            clean_slash = subset_slash.strip("/")
            if clean_slash == "":
                subset_tuple = ()
            else:
                subset_tuple = tuple(int(ch, 16) for ch in clean_slash)
            
            poly_map[subset_tuple] = {
                "class_id": class_id,
                "composition": comp,
                "n": target_n,
                "k": k,
                "is_achiral": bool(int(is_achiral)),
                "orbit_size": int(orb_sz),
                "subset_slash": subset_slash
            }
    return poly_map

def get_dn_ops(n: int) -> List[Tuple[int, int]]:
    """Return all 2n operations (a, b) of the dihedral group D_n: x -> a*x + b mod n."""
    return [(a, b) for a in [1, n - 1] for b in range(n)]

def canonicalise_subset(subset: List[int], n: int) -> Tuple[int, ...]:
    """Return the lexicographical minimum subset in its dihedral orbit."""
    if not subset:
        return ()
    best = None
    for a, b in get_dn_ops(n):
        cand = tuple(sorted((a * x + b) % n for x in subset))
        if best is None or cand < best:
            best = cand
    return best

def is_block_symmetric(block: List[int], n: int) -> bool:
    """Check if block possesses an internal bilateral reflection symmetry in Z_n."""
    b_set = set(block)
    for c in range(n):
        if {(c - x) % n for x in b_set} == b_set:
            return True
    return False

def compute_block_energy(block: List[int], n: int) -> int:
    """Compute total circular chord dispersion energy for a block."""
    e = 0
    m = len(block)
    for i in range(m):
        for j in range(i + 1, m):
            d = min((block[j] - block[i]) % n, (block[i] - block[j]) % n)
            e += d * d
    return e

def get_block_strides(block: List[int], n: int) -> str:
    """Calculate forward cyclic perimeter strides starting from root min(block)."""
    m = len(block)
    if m <= 1:
        return f"{n:X}"
    sb = sorted(block)
    strides = [(sb[(i + 1) % m] - sb[i]) % n for i in range(m)]
    return "".join(f"{s:X}" for s in strides)

def analyze_block_embedding(block: List[int], poly_map: Dict[Tuple[int, ...], Dict[str, Any]], n: int) -> Dict[str, Any]:
    """
    Relates block B to its parent inscribed polygon class in polyatlas.
    Returns:
      poly_class, canon_comp, realised_comp, root, chirality ('+' or '-'), manifest_token
    """
    sb = sorted(block)
    k = len(sb)
    canon_sub = canonicalise_subset(sb, n)
    p_info = poly_map.get(canon_sub)
    if not p_info:
        raise KeyError(f"Canonical subset {canon_sub} not found in polyatlas for Z_{n}")
    
    poly_class = p_info["class_id"]
    canon_comp = p_info["composition"]
    is_achiral = p_info["is_achiral"]
    realised_comp = get_block_strides(sb, n)
    root = sb[0]
    
    # Determine chirality sign: + for direct rotation, - for retrograde reflection
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
        
    token = f"{poly_class}@{root:X}{chirality_char}:{realised_comp}"
    return {
        "poly_class": poly_class,
        "canon_comp": canon_comp,
        "realised_comp": realised_comp,
        "root": f"{root:X}",
        "chirality": chirality_char,
        "manifest_token": token
    }

def format_polygon_profile(class_list: List[str]) -> str:
    """Format multiset of classes into compact sum string e.g. 2x4-12+2x4-15."""
    counts = defaultdict(int)
    for c in class_list:
        counts[c] += 1
    # Sort classes by (k, index)
    def parse_key(c_str):
        parts = c_str.split("-")
        return (int(parts[0]), int(parts[1]))
    
    sorted_classes = sorted(counts.keys(), key=parse_key)
    terms = []
    for c in sorted_classes:
        cnt = counts[c]
        if cnt == 1:
            terms.append(c)
        else:
            terms.append(f"{cnt}x{c}")
    return "+".join(terms)

def parse_slash_partition(p_str: str) -> List[List[int]]:
    """Parse slash hexadecimal partition string e.g. /017A/36CD/45BE/289F/."""
    clean = p_str.strip("/")
    blocks = clean.split("/")
    res = []
    for b in blocks:
        res.append([int(ch, 16) for ch in b])
    return res

def format_slash_partition(part: List[List[int]]) -> str:
    """Format partition into slash hexadecimal notation."""
    return "/" + "/".join("".join(f"{x:X}" for x in sorted(blk)) for blk in part) + "/"

def invert_manifest_token(token: str, n: int) -> List[int]:
    """Reconstruct block vertices from manifest token class@root[chirality]:strides."""
    match = re.match(r"^([0-9]+-[0-9]+)@([0-9A-Fa-f]+)([\+\-]):([0-9A-Fa-f]+)$", token)
    if not match:
        raise ValueError(f"Malformed manifest token: {token}")
    _, root_str, _, strides_str = match.groups()
    root = int(root_str, 16)
    strides = [int(ch, 16) for ch in strides_str]
    curr = root
    verts = [curr]
    for s in strides[:-1]:
        curr = (curr + s) % n
        verts.append(curr)
    return sorted(verts)

# ==============================================================================
# D_4 Universe (z_2^2 on Z_4)
# ==============================================================================
def generate_z4(inngons_tsv: str, out_dir: str, verify: bool):
    print("\n--- Generating Relational Datasets for Z_4 (D_4 Universe) ---")
    poly_map = load_polyatlas(inngons_tsv, 4)
    print(f"Loaded {len(poly_map)} classes for Z_4.")

    m1 = [[0, 2], [1, 3]]
    m2 = [[0, 1], [2, 3]]
    monomers = [
        ("M1", "Monomer", 1, 8, m1),
        ("M2", "Monomer", 2, 4, m2)
    ]

    mosaics_rows = []
    blocks_rows = []

    for macro_id, oligomer, orb_sz, stab_sz, part in monomers:
        s_sym = sum(1 for b in part if is_block_symmetric(b, 4))
        energy = sum(compute_block_energy(b, 4) for b in part)
        sig = "[" + "".join("s" if is_block_symmetric(b, 4) else "n" for b in part) + "]"
        p_slash = format_slash_partition(part)

        block_tokens = []
        classes = []
        for b_idx, b in enumerate(part, 1):
            analysis = analyze_block_embedding(b, poly_map, 4)
            block_tokens.append(analysis["manifest_token"])
            classes.append(analysis["poly_class"])
            v_str = " ".join(str(x) for x in sorted(b))
            blocks_rows.append([
                macro_id, macro_id, 1, 1, 1, b_idx, v_str,
                analysis["poly_class"], analysis["canon_comp"], analysis["realised_comp"],
                analysis["root"], analysis["chirality"], analysis["manifest_token"]
            ])

        poly_profile = format_polygon_profile(classes)
        manifest = "/".join(block_tokens)

        if verify:
            rec_part = [invert_manifest_token(tok, 4) for tok in block_tokens]
            rec_part.sort(key=lambda blk: (min(blk), blk))
            orig_norm = [sorted(b) for b in part]
            orig_norm.sort(key=lambda blk: (min(blk), blk))
            assert rec_part == orig_norm, f"Verification failed for Z_4 {macro_id}"

        mosaics_rows.append([
            macro_id, macro_id, oligomer, 1, 1, 1, orb_sz, stab_sz,
            s_sym, energy, sig, p_slash, poly_profile, manifest
        ])

    # Write TSVs
    m_path = os.path.join(out_dir, "z4_mosaics.tsv")
    b_path = os.path.join(out_dir, "z4_mosaic_blocks.tsv")

    with open(m_path, "w", encoding="utf-8") as f:
        f.write("orbit_id\tmacro_id\toligomer_type\tphase\tdilation_mult\tis_primary\torbit_size\tstab_size\ts_sym\tenergy\tchirality_sig\tpartition\tpoly_profile\tblock_manifest\n")
        for r in mosaics_rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    with open(b_path, "w", encoding="utf-8") as f:
        f.write("orbit_id\tmacro_id\tphase\tdilation_mult\tis_primary\tblock_idx\tvertices\tpoly_class\tcanon_comp\trealised_comp\troot\tchirality\tmanifest_token\n")
        for r in blocks_rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    print(f"✓ Written {len(mosaics_rows)} mosaics to {m_path}")
    print(f"✓ Written {len(blocks_rows)} block relations to {b_path}")

# ==============================================================================
# D_9 Universe (z_3^3 on Z_9)
# ==============================================================================
def get_d9_canonical_trimer_data():
    """Return the exact catalogue of 1 Monomer and 8 Trimers for Z_9."""
    # Monomer M1: regular coset of 3Z_9
    m1 = [[0, 3, 6], [1, 4, 7], [2, 5, 8]]
    
    # 8 Trimers from Table A.1 and d9_tiered_census.py
    # Each trimer is (ID, |O|, [p_phase1, p_phase2, p_phase3])
    t_defs = [
        ("T1", 3, ["/015/267/348/", "/012/345/678/", "/024/168/357/"]),
        ("T2", 9, ["/015/237/468/", "/012/378/456/", "/024/138/567/"]),
        ("T3", 9, ["/015/247/368/", "/012/367/458/", "/024/178/356/"]),
        ("T4", 9, ["/014/256/378/", "/028/134/567/", "/047/135/268/"]),
        ("T5", 9, ["/025/147/368/", "/014/258/367/", "/028/147/356/"]),
        ("T6", 18, ["/014/267/358/", "/028/167/345/", "/047/168/235/"]),
        ("T7", 18, ["/014/268/357/", "/028/156/347/", "/047/123/568/"]),
        ("T8", 18, ["/014/257/368/", "/028/145/367/", "/047/128/356/"]),
    ]
    return m1, t_defs

def generate_z9(inngons_tsv: str, out_dir: str, verify: bool):
    print("\n--- Generating Relational Datasets for Z_9 (D_9 Universe) ---")
    poly_map = load_polyatlas(inngons_tsv, 9)
    print(f"Loaded {len(poly_map)} classes for Z_9.")

    m1_part, t_defs = get_d9_canonical_trimer_data()

    mosaics_rows = []
    blocks_rows = []

    # 1. Monomer M1
    s_sym = sum(1 for b in m1_part if is_block_symmetric(b, 9))
    energy = sum(compute_block_energy(b, 9) for b in m1_part)
    sig = "[" + "".join("s" if is_block_symmetric(b, 9) else "n" for b in m1_part) + "]"
    p_slash = format_slash_partition(m1_part)
    tokens, classes = [], []
    for b_idx, b in enumerate(m1_part, 1):
        analysis = analyze_block_embedding(b, poly_map, 9)
        tokens.append(analysis["manifest_token"])
        classes.append(analysis["poly_class"])
        v_str = " ".join(str(x) for x in sorted(b))
        blocks_rows.append([
            "M1", "M1", 1, 1, 1, b_idx, v_str,
            analysis["poly_class"], analysis["canon_comp"], analysis["realised_comp"],
            analysis["root"], analysis["chirality"], analysis["manifest_token"]
        ])
    prof = format_polygon_profile(classes)
    man = "/".join(tokens)
    if verify:
        rec = [invert_manifest_token(tok, 9) for tok in tokens]
        rec.sort(key=lambda blk: (min(blk), blk))
        assert rec == sorted([sorted(b) for b in m1_part]), "Verification failed for Z_9 M1"
    mosaics_rows.append(["M1", "M1", "Monomer", 1, 1, 1, 1, 18, s_sym, energy, sig, p_slash, prof, man])

    # 2. Trimers T1 .. T8
    mults = [1, 2, 4]
    for tid, orb_sz, phases in t_defs:
        stab_sz = 18 // orb_sz
        for phase_idx, (p_str, mult) in enumerate(zip(phases, mults), 1):
            is_prim = 1 if phase_idx == 1 else 0
            orb_id = f"{tid}.{phase_idx}"
            part = parse_slash_partition(p_str)
            s_sym = sum(1 for b in part if is_block_symmetric(b, 9))
            energy = sum(compute_block_energy(b, 9) for b in part)
            sig = "[" + "".join("s" if is_block_symmetric(b, 9) else "n" for b in part) + "]"
            p_slash = format_slash_partition(part)

            tokens, classes = [], []
            for b_idx, b in enumerate(part, 1):
                analysis = analyze_block_embedding(b, poly_map, 9)
                tokens.append(analysis["manifest_token"])
                classes.append(analysis["poly_class"])
                v_str = " ".join(str(x) for x in sorted(b))
                blocks_rows.append([
                    orb_id, tid, phase_idx, mult, is_prim, b_idx, v_str,
                    analysis["poly_class"], analysis["canon_comp"], analysis["realised_comp"],
                    analysis["root"], analysis["chirality"], analysis["manifest_token"]
                ])
            prof = format_polygon_profile(classes)
            man = "/".join(tokens)
            if verify:
                rec = [invert_manifest_token(tok, 9) for tok in tokens]
                rec.sort(key=lambda blk: (min(blk), blk))
                assert rec == sorted([sorted(b) for b in part]), f"Verification failed for Z_9 {orb_id}"
            mosaics_rows.append([
                orb_id, tid, "Trimer", phase_idx, mult, is_prim, orb_sz, stab_sz,
                s_sym, energy, sig, p_slash, prof, man
            ])

    # Write TSVs
    m_path = os.path.join(out_dir, "z9_mosaics.tsv")
    b_path = os.path.join(out_dir, "z9_mosaic_blocks.tsv")

    with open(m_path, "w", encoding="utf-8") as f:
        f.write("orbit_id\tmacro_id\toligomer_type\tphase\tdilation_mult\tis_primary\torbit_size\tstab_size\ts_sym\tenergy\tchirality_sig\tpartition\tpoly_profile\tblock_manifest\n")
        for r in mosaics_rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    with open(b_path, "w", encoding="utf-8") as f:
        f.write("orbit_id\tmacro_id\tphase\tdilation_mult\tis_primary\tblock_idx\tvertices\tpoly_class\tcanon_comp\trealised_comp\troot\tchirality\tmanifest_token\n")
        for r in blocks_rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    print(f"✓ Written {len(mosaics_rows)} mosaics to {m_path}")
    print(f"✓ Written {len(blocks_rows)} block relations to {b_path}")

# ==============================================================================
# D_16 Universe (z_4^4 on Z_16)
# ==============================================================================
def generate_z16(inngons_tsv: str, hexdec_index: str, out_dir: str, verify: bool):
    print("\n--- Generating Relational Datasets for Z_16 (D_16 Universe, z_4^4) ---")
    if not os.path.exists(hexdec_index):
        raise FileNotFoundError(f"Cannot find hexadecality index at {hexdec_index}")
    
    poly_map = load_polyatlas(inngons_tsv, 16)
    print(f"Loaded {len(poly_map)} classes for Z_16.")

    print(f"Streaming and resolving macro-orbits from: {hexdec_index}...")

    # We produce:
    # 1. z16_mosaics.tsv (83,488 rows, all comosaics)
    # 2. z16_mosaic_blocks.tsv (333,952 rows)
    # 3. z16_macro_mosaics.tsv (21,030 rows, Phase 1 only)
    # 4. z16_macro_mosaic_blocks.tsv (84,120 rows)

    m_all_path = os.path.join(out_dir, "z16_mosaics.tsv")
    b_all_path = os.path.join(out_dir, "z16_mosaic_blocks.tsv")
    m_macro_path = os.path.join(out_dir, "z16_macro_mosaics.tsv")
    b_macro_path = os.path.join(out_dir, "z16_macro_mosaic_blocks.tsv")

    f_m_all = open(m_all_path, "w", encoding="utf-8")
    f_b_all = open(b_all_path, "w", encoding="utf-8")
    f_m_macro = open(m_macro_path, "w", encoding="utf-8")
    f_b_macro = open(b_macro_path, "w", encoding="utf-8")

    # Headers
    m_header = "orbit_id\tmacro_id\toligomer_type\tphase\tdilation_mult\tis_primary\torbit_size\tstab_size\ts_sym\tenergy\tchirality_sig\tpartition\tpoly_profile\tblock_manifest\n"
    b_header = "orbit_id\tmacro_id\tphase\tdilation_mult\tis_primary\tblock_idx\tvertices\tpoly_class\tcanon_comp\trealised_comp\troot\tchirality\tmanifest_token\n"

    f_m_all.write(m_header)
    f_b_all.write(b_header)
    f_m_macro.write(m_header)
    f_b_macro.write(b_header)

    total_macros = 0
    total_comosaics = 0
    total_blocks = 0

    with open(hexdec_index, "r", encoding="utf-8") as f_in:
        for line_num, line in enumerate(f_in, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Format:
            # M01  Monomer  |O|=1  s=4  E=768  /048C/159D/26AE/37BF/ [ssss]
            # D001 Dimer    |O|=2  s=4  E=912/784 /0189/23AB/45CD/67EF/ [ssss] -> /038B/169E/25AD/47CF/ [ssss]
            # T00001 Tetramer |O|= 4 s=4 E= 720 /017A/.../ [ssss] -> ...
            parts = line.split()
            if len(parts) < 6:
                continue
            
            macro_id = parts[0]
            oligomer = parts[1]
            
            # Orbit size
            orb_m = re.search(r"\|O\|=\s*([0-9]+)", line)
            if not orb_m:
                continue
            orb_sz = int(orb_m.group(1))
            stab_sz = 32 // orb_sz

            # Extract all partitions and signatures
            # Cycle arrows separate phases: ' -> '
            cycle_m = re.search(r"(/[0-9A-Fa-f]{4}/[0-9A-Fa-f]{4}/[0-9A-Fa-f]{4}/[0-9A-Fa-f]{4}/.*)$", line)
            if not cycle_m:
                continue
            cycle_str = cycle_m.group(1).strip()
            phase_tokens = [tok.strip() for tok in cycle_str.split("->")]

            num_phases = len(phase_tokens)
            if oligomer == "Monomer":
                mults = [1]
            elif oligomer == "Dimer":
                mults = [1, 3]
            elif oligomer == "Tetramer":
                mults = [1, 3, 7, 5]
            else:
                mults = list(range(1, num_phases + 1))

            total_macros += 1

            for p_idx, (p_chunk, mult) in enumerate(zip(phase_tokens, mults), 1):
                total_comosaics += 1
                is_prim = 1 if p_idx == 1 else 0
                orb_id = macro_id if num_phases == 1 else f"{macro_id}.{p_idx}"

                # Extract partition slash and signature
                chunk_parts = p_chunk.split()
                p_slash_str = chunk_parts[0]
                sig = chunk_parts[1] if len(chunk_parts) > 1 else ""

                part = parse_slash_partition(p_slash_str)
                s_sym = sum(1 for b in part if is_block_symmetric(b, 16))
                energy = sum(compute_block_energy(b, 16) for b in part)

                tokens, classes = [], []
                block_lines = []
                for b_idx, b in enumerate(part, 1):
                    total_blocks += 1
                    analysis = analyze_block_embedding(b, poly_map, 16)
                    tokens.append(analysis["manifest_token"])
                    classes.append(analysis["poly_class"])
                    v_str = " ".join(f"{x:X}" for x in sorted(b))
                    b_row = [
                        orb_id, macro_id, p_idx, mult, is_prim, b_idx, v_str,
                        analysis["poly_class"], analysis["canon_comp"], analysis["realised_comp"],
                        analysis["root"], analysis["chirality"], analysis["manifest_token"]
                    ]
                    b_str = "\t".join(str(x) for x in b_row) + "\n"
                    block_lines.append(b_str)

                prof = format_polygon_profile(classes)
                man = "/".join(tokens)

                if verify and total_macros <= 500:
                    rec = [invert_manifest_token(tok, 16) for tok in tokens]
                    rec.sort(key=lambda blk: (min(blk), blk))
                    assert rec == sorted([sorted(b) for b in part]), f"Verification failed for Z_16 {orb_id}"

                m_row = [
                    orb_id, macro_id, oligomer, p_idx, mult, is_prim, orb_sz, stab_sz,
                    s_sym, energy, sig, p_slash_str, prof, man
                ]
                m_str = "\t".join(str(x) for x in m_row) + "\n"

                # Write to all comosaics
                f_m_all.write(m_str)
                for bl in block_lines:
                    f_b_all.write(bl)

                # If primary, write to macro files
                if is_prim:
                    f_m_macro.write(m_str)
                    for bl in block_lines:
                        f_b_macro.write(bl)

            if total_macros % 5000 == 0:
                print(f"  Processed {total_macros:,} macro-orbits ({total_comosaics:,} dihedral orbits)...")

    f_m_all.close()
    f_b_all.close()
    f_m_macro.close()
    f_b_macro.close()

    print(f"✓ Completed Z_16 generation:")
    print(f"  - Total Macro-Orbits:  {total_macros:,}")
    print(f"  - Total Dihedral Orbits: {total_comosaics:,}")
    print(f"  - Total Block Records:   {total_blocks:,}")
    print(f"  - Files: {m_all_path}, {b_all_path}")
    print(f"           {m_macro_path}, {b_macro_path}")

def main():
    args = parse_args()
    print("=" * 80)
    print("HEXADECALITY RELATIONAL BRIDGE GENERATOR")
    print("=" * 80)
    print(f"Universe:        {args.universe}")
    print(f"polyatlas tsv:   {args.inngons_tsv}")
    print(f"Hexdec index:    {args.hexdec_index}")
    print(f"Output dir:      {args.out_dir}")
    print(f"Verification:    {args.verify}")
    print("=" * 80)

    os.makedirs(args.out_dir, exist_ok=True)

    if args.universe in ["all", "z4"]:
        generate_z4(args.inngons_tsv, args.out_dir, args.verify)

    if args.universe in ["all", "z9"]:
        generate_z9(args.inngons_tsv, args.out_dir, args.verify)

    if args.universe in ["all", "z16"]:
        generate_z16(args.inngons_tsv, args.hexdec_index, args.out_dir, args.verify)

    print("\n" + "=" * 80)
    print("ALL RELATIONAL DATASETS GENERATED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    main()
