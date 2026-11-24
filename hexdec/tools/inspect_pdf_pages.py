#!/usr/bin/env python3
"""
inspect_pdf_pages.py - Inspect page breakdown and content markers in generated PDF documents.

Author: Gemma Knee
"""

import sys
import subprocess

def inspect_pdf(pdf_path, search_terms):
    cmd = ["pdftotext", pdf_path, "-"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    pages = res.stdout.split("\x0c")
    print(f"Total pages in {pdf_path}: {len(pages)-1}")
    for idx, page_text in enumerate(pages[:-1], 1):
        for term in search_terms:
            if term.lower() in page_text.lower():
                # Extract first line matching
                matched_line = [l.strip() for l in page_text.splitlines() if term.lower() in l.lower()][0]
                print(f"Page {idx:2d}: Matched '{term}' -> {matched_line[:60]}")

if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else "hexdec/hexadecality.pdf"
    terms = ["Appendix A", "Appendix B", "Figure A.1", "Figure A.2", "Contents"]
    inspect_pdf(pdf, terms)
