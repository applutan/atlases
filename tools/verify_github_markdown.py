#!/usr/bin/env python3
"""
verify_github_markdown.py
Audits all markdown files in notes/ against GitHub's live /markdown rendering API.
"""

import sys
import os
import subprocess
import glob
import re
from bs4 import BeautifulSoup

def test_file(file_path, verbose=False):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    result = subprocess.run(
        ["gh", "api", "/markdown", "--method", "POST",
         "-f", f"text={content}",
         "-f", "mode=gfm",
         "-f", "context=applutan/composit"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Error querying GitHub API for {file_path}: {result.stderr}")
        return False

    html = result.stdout
    soup = BeautifulSoup(html, "html.parser")
    
    issues = []
    
    if verbose:
        print(f"\n--- Verbose Inspection for {file_path} ---")
        img_tags = soup.find_all("img")
        print(f"Found {len(img_tags)} <img> tags:")
        for img in img_tags:
            print(f"  • src={img.get('src')}, width={img.get('width')}, alt={img.get('alt')}")

    
    # Check 1: Check for unparsed raw display math in paragraphs outside math-renderer
    for p in soup.find_all("p"):
        if "$$" in p.text and not p.find("math-renderer", class_="js-display-math"):
            issues.append(f"Unparsed display math block ($$) in paragraph: '{p.text.strip()[:60]}...'")

    # Check 2: Check for unparsed table syntax |---| or | :---
    text_content = soup.get_text()
    for line in text_content.splitlines():
        if "|---|" in line or "| :---" in line or "|:---" in line:
            issues.append(f"Broken/unparsed table header: '{line.strip()[:60]}'")

    # Check 3: Check for unsupported macros or KaTeX errors
    if "\\operatorname" in content:
        issues.append("Forbidden macro '\\operatorname' found (use '\\mathrm' or '\\text')")

    if "\\sb" in content or "\\sp" in content:
        issues.append("Forbidden TeX primitive '\\sb' or '\\sp' found (KaTeX does not support '\\sb'/''\\sp'; use '_' and '^')")

    if "\\begin{aligned}" in content or "\\begin{align" in content:
        issues.append("Forbidden '\\begin{aligned}' or 'align' environment found (CommonMark collapses '\\\\' into single '\\', causing KaTeX failure; decompose into separate '$$' equations)")

    # Check 3a: Check for bold/italic math boundary collisions (**$, $**, *$, $*)
    for line_idx, line in enumerate(content.splitlines()):
        if "**$" in line or "$**" in line:
            issues.append(f"Line {line_idx+1}: Bold-math delimiter collision ('**$' or '$**'); keep math outside asterisks")

    # Check 3a2: Check for trailing display punctuation before closing $$
    for line_idx, line in enumerate(content.splitlines()):
        if re.search(r'[.,]\s*\$\$$', line.strip()):
            issues.append(f"Line {line_idx+1}: Trailing punctuation before closing '$$' (terminal punctuation bacilli)")

    # Check 3a3: Check for hyphenated math collisions ($-word or word-$)
    for line_idx, line in enumerate(content.splitlines()):
        if re.search(r'\$[^$\n]+\$-[a-zA-Z0-9]', line) or re.search(r'[a-zA-Z0-9]-\$[^$\n]+\$', line):
            issues.append(f"Line {line_idx+1}: Hyphenated math delimiter collision (e.g. '$n$-gon'); GitHub client-side KaTeX treats '$-' as a price range and drops math rendering (use '$n\\text{{-gon}}$' instead)")
    
    # Check for unescaped underscores inside \text{...}
    text_matches = re.findall(r'\\text\{([^}]+)\}', content)
    for tm in text_matches:
        if "_" in tm and "\\_" not in tm:
            issues.append(f"Unescaped underscore in \\text{{{tm}}} (causes KaTeX error)")

    # Check 3b: Check for unescaped pipe '|' in math expressions inside Markdown table lines
    for line_idx, line in enumerate(content.splitlines()):
        if line.strip().startswith("|"):
            m_spans = re.findall(r"\$([^$]+)\$", line)
            for ms in m_spans:
                if "|" in ms:
                    issues.append(f"Line {line_idx+1}: Unescaped pipe '|' in table math '${ms}$' (use '\\vert' or '\\lvert/\\rvert')")

    # Check 3c: Check for LaTeX newline bracket spacing '\\[...]' which triggers GFM display math collision
    if "\\\\[" in content:
        issues.append(r"Forbidden LaTeX newline bracket spacing '\\\[' found (causes KaTeX '\[' display math collision in GFM; use clean '\\')")

    # Check 4: Check for HTML em tags corrupting math inside paragraphs/lists
    # Decompose valid math-renderer tags first so legitimate text italics are not conflated with math
    soup_clean = BeautifulSoup(html, "html.parser")
    for m in soup_clean.find_all("math-renderer"):
        m.decompose()

    for tag in soup_clean.find_all(["p", "li", "td", "th"]):
        text_tag = str(tag)
        if "<em>" in text_tag and ("\\mathcal" in text_tag or "\\mathbf" in text_tag or "\\phi" in text_tag or "t^" in text_tag or "\\mathrm" in text_tag or "\\mathbb" in text_tag):
            issues.append(f"CommonMark italics '<em>' corrupted math in: {tag.text[:60]}...")

    # Check 4b: Check for any unrendered '$' remaining anywhere outside math-renderer or code blocks
    for pre in soup_clean.find_all(["pre", "code"]):
        pre.decompose()

    for line in soup_clean.get_text().splitlines():
        if "$" in line:
            issues.append(f"Unrendered math delimiter '$' in: {line.strip()}")

    # Report
    if issues:
        print(f"❌ {file_path} had {len(issues)} rendering issue(s):")
        for iss in issues:
            print(f"   • {iss}")
        return False
    else:
        math_count = len(soup.find_all("math-renderer"))
        table_count = len(soup.find_all("table"))
        print(f"✓ {file_path:52} OK ({math_count:2d} math tags, {table_count} tables)")
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit Markdown files against GitHub's live rendering API.")
    parser.add_argument("files", nargs="*", help="Optional specific Markdown files to verify. If omitted, checks notes/*.md, PROJECT_CONTEXT.md, README.md.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose tag details (images, headers)")
    args = parser.parse_args()

    if args.files:
        notes = args.files
    else:
        notes = sorted(glob.glob("notes/*.md") + ["PROJECT_CONTEXT.md", "README.md"])

    all_ok = True
    for note in notes:
        ok = test_file(note, verbose=args.verbose)
        if not ok:
            all_ok = False
            
    if all_ok:
        print("\n🎉 ALL CHECKED MARKDOWN FILES RENDER PERFECTLY ON GITHUB!")
    else:
        print("\n⚠️ Some markdown files have rendering issues.")

if __name__ == "__main__":
    main()
