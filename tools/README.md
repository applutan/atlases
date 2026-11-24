# Atlases Common Toolchain & Verification Suite

This directory contains the cross-cutting algebraic engines, quality-assurance auditors, and multi-media translation tools shared across all three volumes of the cyclic lattice cartography trilogy (*The Polygonal Burnsidean*, *Hexadecality*, and *An Atlas of Composition Mosaics*).

All utilities provide standardised command-line parameterisation via `--help` documentation and support non-destructive batch processing.

---

## 1. Editorial & Quality Assurance Suite

### `audit_british_spelling.py`
Enforces British English spelling conventions across all LaTeX monograph sources in the repository:
* Audits `-ise`/`-isation` (e.g. *realise*, *factorisation*, *characterisation*, *stabiliser*, *normalised*) and British orthography (*behaviour*, *catalogue*).
* Automatically audits all three monographs when invoked without arguments:
```bash
python3 tools/audit_british_spelling.py
```
* Or targets specific files/directories:
```bash
python3 tools/audit_british_spelling.py polyatlas/sec unimosatlas/sec allmosatlas/sec
```

### `audit_display_math.py`
Guarantees that standalone display math environments (`equation`, `align`, or bracket displays) are clean and completely free of terminal punctuation bacilli (`.` or `,`) per strict styling guidelines:
```bash
python3 tools/audit_display_math.py
```

### `verify_github_markdown.py`
Validates that all GitHub Markdown documentation (`README.md` files) adheres to GitHub's KaTeX math delimiter syntax and standard pipe table rules:
```bash
python3 tools/verify_github_markdown.py \
  README.md \
  polyatlas/data/README.md \
  unimosatlas/data/README.md \
  unimosatlas/tools/README.md \
  allmosatlas/README.md \
  allmosatlas/data/README.md \
  allmosatlas/tools/README.md \
  tools/README.md
```

---

## 2. Algebraic & Macro-Orbit Engines

### `affine_macro_orbits.py`
Computes the exact affine macro-orbit inventory of equal-block set partitions on any ambient cyclic ring $\mathbb{Z}_n$ under the outer automorphism quotient group:

$$G_{\mathrm{macro}} = \mathrm{Aff}(\mathbb{Z}_n) / D_n \cong (\mathbb{Z}_n)^\times / \{\pm 1\}$$

Accepts arbitrary ambient dimensions $n$, block size $k$, and block count $s$:
```bash
# Compute affine macro-orbits on Z_16 (k=4, s=4)
python3 tools/affine_macro_orbits.py -n 16 -k 4 -s 4

# Compute affine macro-orbits on Z_9 (k=3, s=3)
python3 tools/affine_macro_orbits.py -n 9 -k 3 -s 3
```

---

## 3. Musical Translation & Engraving Suite

Translates the geometric and combinatorial structure of cyclic partitions into multi-voice polyrhythmic percussion scores and MIDI performances. See the complete reference manual in [`PERCUSSION_SUITE.md`](PERCUSSION_SUITE.md) for full acoustic voice mappings, metric pulse groupings, and advanced CLI parameters.

### Interlocking MIDI Synthesizer (`midipartner.py`)
Generates multi-track MIDI performances from canonical partition strings across any circular lattice $\mathbb{Z}_n$:
```bash
python3 tools/midipartner.py -p "/0279/18AF/35CE/46BD/" -o loop.mid --bpm 120 -b 4
```

### W3C MusicXML Engraver (`xmusicpartner.py`)
Translates partition strings directly into notation-ready W3C MusicXML percussion scores for import into MuseScore, Finale, or Sibelius:
```bash
python3 tools/xmusicpartner.py -p "/0279/18AF/35CE/46BD/" -o score.musicxml --score-type multi
```
