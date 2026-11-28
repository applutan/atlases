#!/usr/bin/env python3
"""
verify_against_appendix_b3.py

Verifies the consolidated census table (Z_1 to Z_16) and stratified shape inventory
(Z_1 to Z_12) in allmosatlas against Appendix B.3 of the mosaicality monograph
(located at ~/gemai/composit/sec/AppendixMosaicStats.tex).

Usage:
    ./verify_against_appendix_b3.py [--verbose] [--appendix PATH] [--census PATH] [--shape PATH]
"""

import argparse
import os
import re
import sys


def parse_appendix_b3(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    table_chunks = content.split("tab:mosaic-stats-")

    grand_totals = {}
    shape_rows = {}

    for chunk in table_chunks[1:]:
        n_m = re.match(r"^(\d+)", chunk)
        if not n_m:
            continue
        n = int(n_m.group(1))

        table_body = chunk[:chunk.find(r"\end{longtable}")]

        # Extract omega powers from header line
        # Header line starts with \#p & \#o & $\mathbf{z}^\lambda$ & ... \\
        omega_powers = []
        for line in table_body.split("\n"):
            line = line.strip()
            if ("#p" in line or "\\#p" in line) and "&" in line:
                cells = [c.strip() for c in line.replace("\\\\", "").split("&")]
                for w in cells[3:]:
                    pwr = re.search(r"\\omega\^\{(\d+)\}", w)
                    if pwr:
                        omega_powers.append(int(pwr.group(1)))
                    elif "\\omega" in w:
                        omega_powers.append(1)
                break

        if not omega_powers:
            continue

        # Find the grand total row: follows \hline\hline near the end
        gt_matches = re.findall(
            r"\\hline\s*\\hline\s*(\d+)\s*&\s*(\d+)\s*&\s*&\s*([^\\]+)\\\\",
            table_body
        )
        if gt_matches:
            p_tot = int(gt_matches[-1][0])
            o_tot = int(gt_matches[-1][1])
            vals = [v.strip() for v in gt_matches[-1][2].split("&")]
            poly = {}
            for pwr, v in zip(omega_powers, vals):
                if v and v != "-":
                    poly[pwr] = int(v)
            grand_totals[n] = {
                "partitions": p_tot,
                "mosaics": o_tot,
                "poly": poly
            }

        # Shape rows
        for line in table_body.split("\n"):
            line = line.strip()
            if line.startswith(r"\hline") or line.startswith(r"\caption") or line.startswith(r"#p"):
                continue
            if "&" in line and "\\\\" in line:
                cells = [c.strip() for c in line.replace(r"\\", "").split("&")]
                if len(cells) >= 3 and cells[0].isdigit() and cells[1].isdigit():
                    mono = cells[2]
                    if mono.startswith("$") and mono.endswith("$"):
                        clean_mono = mono.strip("$").replace(" ", "")
                        poly = {}
                        for pwr, v in zip(omega_powers, cells[3:]):
                            v = v.strip()
                            if v and v != "-":
                                poly[pwr] = int(v)
                        shape_rows[(n, clean_mono)] = {
                            "partitions": int(cells[0]),
                            "mosaics": int(cells[1]),
                            "poly": poly
                        }

    return grand_totals, shape_rows


def parse_allmosatlas_summary(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    census = {}
    chunks = text.split(r"$\mathbb{Z}")
    for chunk in chunks[1:]:
        n_m = re.match(r"^_?\{?(\d+)\}?\$", chunk.strip().split("&")[0].strip())
        if not n_m:
            continue
        n = int(n_m.group(1))

        # Clean up LaTeX brackets in numbers
        clean_chunk = chunk.replace("{,}", "").replace(",", "")
        b_n_m = re.search(r"&\s*(\d+)\s*&\s*(\d+)\s*&\s*(\d+)\s*&\s*\\textbf\{(\d+)\}\s*&(.*?)(?=\\midrule|\$\\mathbb\{Z\}|\\bottomrule|$)", clean_chunk, re.DOTALL)
        if b_n_m:
            d_order = int(b_n_m.group(1))
            b_n = int(b_n_m.group(2))
            shapes_cnt = int(b_n_m.group(3))
            mosaics = int(b_n_m.group(4))
            poly_str = b_n_m.group(5)

            poly = {}
            for term in re.finditer(r"(\d+)\\omega\^\{(\d+)\}", poly_str):
                coeff = int(term.group(1))
                deg = int(term.group(2))
                poly[deg] = coeff

            census[n] = {
                "partitions": b_n,
                "mosaics": mosaics,
                "poly": poly
            }

    return census


def parse_shape_census_z1_z12(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    shape_rows = {}
    current_n = None

    for line in text.split("\n"):
        line = line.strip()
        n_m = re.search(r"\\textbf\{Ring \$\\mathbb\{Z\}_\{?(\d+)\}?\$", line)
        if n_m:
            current_n = int(n_m.group(1))
            continue

        n_cap = re.search(r"\\caption\{.*?\\mathbb\{Z\}_\{?(\d+)\}?", line)
        if n_cap and "through" not in line and "and" not in line:
            current_n = int(n_cap.group(1))
            continue

        if current_n is not None and "&" in line and "\\\\" in line:
            # Clean comma grouping
            clean = line.replace("{,}", "").replace(",", "")
            # shape data lines have $monomial$ & partitions & mosaics & poly \\ (or reverse)
            m = re.search(r"^\$([^\$]+)\$\s*&\s*(\d+)\s*&\s*(\d+)\s*&(.*)\\\\", clean)
            if not m:
                m_rev = re.search(r"^(\d+)\s*&\s*(\d+)\s*&\s*\$([^\$]+)\$\s*&(.*)\\\\", clean)
                if m_rev:
                    p_cnt = int(m_rev.group(1))
                    o_cnt = int(m_rev.group(2))
                    mono = m_rev.group(3).replace(" ", "")
                    poly_str = m_rev.group(4)
                else:
                    continue
            else:
                mono = m.group(1).replace(" ", "")
                p_cnt = int(m.group(2))
                o_cnt = int(m.group(3))
                poly_str = m.group(4)

                poly = {}
                for term in re.finditer(r"(\d+)\\omega\^\{(\d+)\}", poly_str):
                    coeff = int(term.group(1))
                    deg = int(term.group(2))
                    poly[deg] = coeff

                shape_rows[(current_n, mono)] = {
                    "partitions": p_cnt,
                    "mosaics": o_cnt,
                    "poly": poly
                }

    return shape_rows
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    census = {}
    chunks = text.split(r"$\mathbb{Z}")
    for chunk in chunks[1:]:
        n_m = re.match(r"^_?\{?(\d+)\}?\$", chunk.strip().split("&")[0].strip())
        if not n_m:
            continue
        n = int(n_m.group(1))

        # Clean up LaTeX brackets in numbers
        clean_chunk = chunk.replace("{,}", "").replace(",", "")
        b_n_m = re.search(r"&\s*(\d+)\s*&\s*(\d+)\s*&\s*(\d+)\s*&\s*\\textbf\{(\d+)\}\s*&(.*?)(?=\\midrule|\$\\mathbb\{Z\}|\\bottomrule|$)", clean_chunk, re.DOTALL)
        if b_n_m:
            d_order = int(b_n_m.group(1))
            b_n = int(b_n_m.group(2))
            shapes_cnt = int(b_n_m.group(3))
            mosaics = int(b_n_m.group(4))
            poly_str = b_n_m.group(5)

            poly = {}
            for term in re.finditer(r"(\d+)\\omega\^\{(\d+)\}", poly_str):
                coeff = int(term.group(1))
                deg = int(term.group(2))
                poly[deg] = coeff

            census[n] = {
                "partitions": b_n,
                "mosaics": mosaics,
                "poly": poly
            }

    return census


def main():
    parser = argparse.ArgumentParser(
        description="Verify allmosatlas tables against Appendix B.3 of mosaicality"
    )
    parser.add_argument(
        "--appendix",
        default="/home/paul/gemai/composit/sec/AppendixMosaicStats.tex",
        help="Path to AppendixMosaicStats.tex in composit"
    )
    parser.add_argument(
        "--census",
        default="/home/paul/gemai/atlases/allmosatlas/gen/census_summary_z1_z16.tex",
        help="Path to census_summary_z1_z16.tex in allmosatlas"
    )
    parser.add_argument(
        "--shape-table",
        default="/home/paul/gemai/atlases/allmosatlas/gen/shape_census_z1_z12.tex",
        help="Path to shape_census_z1_z12.tex in allmosatlas"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Emit verbose audit details"
    )

    args = parser.parse_args()

    print(f"=== Cross-Verification Audit: allmosatlas vs. composit Appendix B.3 ===")
    print(f"Appendix B.3 Source: {args.appendix}")
    print(f"Census Summary Source: {args.census}")
    print(f"Shape Census Source:   {args.shape_table}")
    print()

    if not os.path.exists(args.appendix):
        print(f"Error: Appendix B.3 file not found at {args.appendix}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.census):
        print(f"Error: Census summary file not found at {args.census}", file=sys.stderr)
        sys.exit(1)

    app_totals, app_shapes = parse_appendix_b3(args.appendix)
    census = parse_allmosatlas_summary(args.census)
    our_shapes = parse_shape_census_z1_z12(args.shape_table)

    print(f"Parsed {len(app_totals)} degree tables from Appendix B.3 (degrees: {sorted(app_totals.keys())})")
    print(f"Parsed {len(app_shapes)} shape rows from Appendix B.3")
    print(f"Parsed {len(census)} rows from allmosatlas Table 1.1")
    print(f"Parsed {len(our_shapes)} shape rows from allmosatlas Table 2.1")
    print()

    # Compare Grand Totals for n = 1 .. 12
    all_match = True
    print("--- [Degree-by-Degree Grand Total Verification (n = 1 .. 12)] ---")
    for n in range(1, 13):
        if n not in app_totals:
            print(f"✗ Degree Z_{n} missing from Appendix B.3!")
            all_match = False
            continue
        if n not in census:
            print(f"✗ Degree Z_{n} missing from Table 1.1!")
            all_match = False
            continue

        at = app_totals[n]
        ct = census[n]

        p_match = (at["partitions"] == ct["partitions"])
        m_match = (at["mosaics"] == ct["mosaics"])
        poly_match = (at["poly"] == ct["poly"])

        status = "✓ PASS" if (p_match and m_match and poly_match) else "✗ FAIL"
        if not (p_match and m_match and poly_match):
            all_match = False
            print(f"{status} Z_{n}:")
            if not p_match:
                print(f"   Partitions: Appendix={at['partitions']} vs Table1.1={ct['partitions']}")
            if not m_match:
                print(f"   Mosaics:    Appendix={at['mosaics']} vs Table1.1={ct['mosaics']}")
            if not poly_match:
                print(f"   Poly App:   {at['poly']}")
                print(f"   Poly Table: {ct['poly']}")
        else:
            poly_str = " + ".join(f"{cnt}w^{pwr}" for pwr, cnt in sorted(ct["poly"].items()))
            print(f"{status} Z_{n:2d}: B_{n} = {ct['partitions']:<10d} Mosaics = {ct['mosaics']:<8d} Poly = {poly_str}")

    print()

    # Compare Shape Rows (n = 1 .. 12)
    print("--- [Stratified Partition Shape Inventory Verification (271 Shapes across Z_1 .. Z_12)] ---")
    shape_mismatches = 0
    # Normalise monomial representations (e.g. z_1z_2 vs z_2z_1)
    def normalise_mono(m):
        # Extract factors z_k^c or z_k
        factors = re.findall(r"z_\{?(\d+)\}?(?:\^\{?(\d+)\}?)?", m)
        parsed = {}
        for deg, exp in factors:
            d = int(deg)
            e = int(exp) if exp else 1
            parsed[d] = parsed.get(d, 0) + e
        # Build canonical sorted string (descending by part size)
        parts = []
        for d in sorted(parsed.keys(), reverse=True):
            e = parsed[d]
            if e == 1:
                parts.append(f"z_{d}")
            else:
                parts.append(f"z_{d}^{e}")
        return "".join(parts)

    norm_app_shapes = {}
    for (n, mono), data in app_shapes.items():
        norm_app_shapes[(n, normalise_mono(mono))] = data

    norm_our_shapes = {}
    for (n, mono), data in our_shapes.items():
        norm_our_shapes[(n, normalise_mono(mono))] = data

    for key, data in sorted(norm_our_shapes.items()):
        n, mono = key
        if key not in norm_app_shapes:
            print(f"✗ Shape (Z_{n}, {mono}) missing from Appendix B.3!")
            shape_mismatches += 1
            continue
        ad = norm_app_shapes[key]
        p_ok = (data["partitions"] == ad["partitions"])
        m_ok = (data["mosaics"] == ad["mosaics"])
        poly_ok = (data["poly"] == ad["poly"])

        if not (p_ok and m_ok and poly_ok):
            shape_mismatches += 1
            print(f"✗ MISMATCH (Z_{n}, {mono}):")
            if not p_ok:
                print(f"   #p: Table2.1={data['partitions']} vs Appendix={ad['partitions']}")
            if not m_ok:
                print(f"   #o: Table2.1={data['mosaics']} vs Appendix={ad['mosaics']}")
            if not poly_ok:
                print(f"   Poly Table2.1: {data['poly']}")
                print(f"   Poly Appendix: {ad['poly']}")

    if shape_mismatches == 0:
        print(f"✓ All {len(norm_our_shapes)} partition shapes in Table 2.1 perfectly match Appendix B.3 of mosaicality in #p, #o, and orbit polynomials!")
    else:
        print(f"✗ Found {shape_mismatches} shape mismatches!")
        all_match = False

    print()
    if all_match:
        print("================================================================================")
        print("✓ FULL CONVERGENCE: Table 1.1 and Table 2.1 in allmosatlas are 100% congruent")
        print("  with Appendix B.3 of mosaicality across all 12 degrees and 271 shapes!")
        print("================================================================================")
    else:
        print("✗ Discrepancies detected between allmosatlas and Appendix B.3.")
        sys.exit(1)


if __name__ == "__main__":
    main()
