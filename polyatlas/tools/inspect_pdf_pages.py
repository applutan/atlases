#!/usr/bin/env python3
"""
inspect_pdf_pages.py - Locates specific strings and ring sections within compiled PDF pages.
Accepts CLI arguments via argparse.
"""

import argparse
import subprocess
import sys

def inspect_pdf(pdf_path, find_rings=True, extra_queries=None):
    res = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True, check=True)
    pages = res.stdout.split("\x0c")[:-1]
    total_pages = len(pages)
    print(f"Inspecting '{pdf_path}' ({total_pages} pages)...")

    if find_rings:
        print("\n--- Ring Section Starting Pages ---")
        ring_queries = [
            (3, "The Triangular Ring"),
            (4, "The Tetragonal Ring"),
            (5, "The Pentagonal Ring"),
            (6, "The Hexagonal Ring"),
            (7, "The Heptagonal Ring"),
            (8, "The Octagonal Ring"),
            (9, "The Enneagonal Ring"),
            (10, "The Decagonal Ring"),
            (11, "The Hendecagonal Ring"),
            (12, "The Dodecagonal Ring"),
            (13, "The Tridecagonal Ring"),
            (14, "The Tetradecagonal Ring"),
            (15, "The Pentadecagonal Ring"),
            (16, "The Hexadecagonal Ring"),
        ]
        for n, title in ring_queries:
            found = []
            for p_num, text in enumerate(pages, start=1):
                if title in text:
                    found.append(p_num)
            print(f"Z_{n:02d} ({title}): Plate Page {found[0] if found else 'NOT FOUND'}")

    if extra_queries:
        print("\n--- Custom Queries ---")
        for q in extra_queries:
            matches = [p_num for p_num, text in enumerate(pages, start=1) if q in text]
            print(f"Query '{q}': found on pages {matches}")

def main():
    parser = argparse.ArgumentParser(description="Audit and locate sections in PDF.")
    parser.add_argument("-p", "--pdf", default="polyatlas/plates/poly_plates.pdf", help="Path to PDF")
    parser.add_argument("-q", "--query", nargs="*", help="Extra string queries")
    args = parser.parse_args()

    inspect_pdf(args.pdf, find_rings=True, extra_queries=args.query)

if __name__ == "__main__":
    main()

