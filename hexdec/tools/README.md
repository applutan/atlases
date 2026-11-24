# Hexadecality Computational Toolchain & Atlas Generators

This directory contains the production generators, algebraic classification engines, TikZ figure pipelines, and interactive CLI utilities supporting *Hexadecality: The Atlas of Hexadecagonal Compositions*.

All Python utilities provide standardised command-line parameterisation via `--help`, accept contextual flags, and produce deterministic outputs.

---

## 1. Interactive Classification & Query Tools

### `lookup_mosaic.py`
The primary command-line resolution tool documented in Appendix B of the monograph. Given an arbitrary partition string of $\mathbb{Z}\_{16}$ into 4 equal blocks, it resolves the canonical dihedral representative, stabilizer order, chord dispersion energy, and traces its full 4-phase Galois cycle under $\langle \mu\_3 \rangle$:
```bash
python3 hexdec/tools/lookup_mosaic.py "/0279/18AF/35CE/46BD/"
```

### `affine_macro_orbits.py`
The general mathematical engine computing the macro-orbit structure of set partitions under the outer automorphism group:

$$G\_{\mathrm{macro}} = \mathrm{Aff}(\mathbb{Z}\_n) / D\_n \cong (\mathbb{Z}\_n)^\times / \{\pm 1\}$$

Supports arbitrary ambient cyclic lattices $\mathbb{Z}\_n$ and equal-block shapes $z\_k^m$ via Burnside's Lemma.
```bash
python3 hexdec/tools/affine_macro_orbits.py -n 16 -k 4 -s 4
```

### `analyze_relational_coverage.py`
Audits the injection of equal-block composition comosaics into the dihedral inscribed polygon orbits of `polyatlas`. Reports class coverage, direct vs retrograde enantiomorphic counts, and sorting cascade dispersion:
```bash
python3 hexdec/tools/analyze_relational_coverage.py --blocks-tsv hexdec/data/z16_macro_mosaic_blocks.tsv --inngons-tsv polyatlas/data/inngons.tsv --target-n 16 --target-k 4
```

### `monomer_symmetry_analysis.py`
Computes the exact stabilizer subgroup decomposition, bilateral symmetry count $s \in \{0 \dots 4\}$, and chord dispersion energy $E$ for the 14 Monomers of $\mathbb{Z}\_{16}$:
```bash
python3 hexdec/tools/monomer_symmetry_analysis.py --survey
```

---

## 2. Catalog & Dataset Generators

### `generate_hexdec_relational_data.py`
Generates the normalized, RFC/GitHub-compliant TSV datasets in `hexdec/data/` bridging composition comosaics to `polyatlas` polygon classes. Includes an automatic bijective reconstruction verification flag:
```bash
python3 hexdec/tools/generate_hexdec_relational_data.py --universe all --verify
```

### `extract_doublets.py`
Extracts and serializes all 295 mutually orthogonal partition doublets on $\mathbb{Z}\_{16}$ into `hexdec/data/doublets.json`:
```bash
python3 hexdec/tools/extract_doublets.py -o hexdec/data/doublets.json
```

### `generate_all_tetramers.cpp` / `generate_all_tetramers`
High-performance C++ enumerator generating the complete master index `hexdec/data/hexadecality_index.txt` ($21{,}065$ lines) and `hexdec/data/tetramers_full_index.txt` ($20{,}721$ 4-cycles) via the 5-tier natural sorting cascade:
```bash
g++ -O3 -std=c++17 hexdec/tools/generate_all_tetramers.cpp -o hexdec/tools/generate_all_tetramers
./hexdec/tools/generate_all_tetramers
```

### `build_tetramers_atlas.cpp` / `build_tetramers_atlas`
High-performance C++ compiler that generates the modular LaTeX plate chunks `hexdec/plates/tetramers_part1.tex` through `part4.tex` containing 216 plates of cartouched tetramer comosaics:
```bash
g++ -O3 -std=c++17 hexdec/tools/build_tetramers_atlas.cpp -o hexdec/tools/build_tetramers_atlas
./hexdec/tools/build_tetramers_atlas
```

### `generate_dimers_plates.py`
Generates the complete 7-page visual catalogue `hexdec/plates/dimers_atlas.tex` displaying all 295 Dimers (2-cycles under $\mu\_3$):
```bash
python3 hexdec/tools/generate_dimers_plates.py --cols 3 --rows 14
```

### `generate_doublets_plates.py`
Generates the companion visual plates for mutually orthogonal partition doublets:
```bash
python3 hexdec/tools/generate_doublets_plates.py
```

### `compile_atlas_parts.sh` & `render_atlas_samples.sh`
Shell automation scripts for parallel LaTeX compilation of tetramer plate chunks and raster sampling of visual plates.

---

## 3. Cartographic & TikZ Figure Pipelines

| Utility | Description | Default Output |
| :--- | :--- | :--- |
| `generate_cover_art.py` | Generates high-density TikZ cover art cartouches | `hexdec/tkz/fig_cover_t10360.tkz`, `fig_cover_t20721.tkz` |
| `generate_intro_figures.py` | Generates clock-face convention and dilation stages | `hexdec/tkz/T00646.tkz`, `hexdec/tkz/T00646-1-dil.tkz` |
| `generate_monomer_tikz.py` | Renders the 2-row visual plate of all 14 Monomers | `hexdec/tkz/fig_14_monomers.tkz` |
| `generate_cartouche_sample.py` | Generates prototype cartouched 4-cycle linear strips | `hexdec/tkz/fig_cartouche_sample.tkz` |
| `generate_sample_plate_tikz.py` | Renders linear cartouche row with directed cycling arrows | `hexdec/tkz/fig_sample_plate.tkz` |
| `generate_small_universes.py` | Generates TikZ plates for Appendix A ($D\_4$ and $D\_9$) | `hexdec/tkz/fig_d4_universe.tkz`, `fig_d9_universe.tkz` |
| `generate_tetramer_scale_comparison.py`| Renders the 3-tier comparative publishing density plate | `hexdec/tkz/fig_tetramer_scale_comparison.tkz` |

---

## 4. Musical Engraving & Audio Synthesis (Shared Toolsuite)

Symlinked into the project-wide toolchain at [`atlases/tools/`](../../tools/):

* **`midipartner.py`** (aliased as `midipart` / `partition_to_midi.py`):
  Synthesizes any valid mosaic partition into a multi-track General MIDI percussion loop on Channel 10:
  ```bash
  python3 hexdec/tools/midipartner.py -p "/0279/18AF/35CE/46BD/" -o loop.mid --bpm 120 -b 4
  ```

* **`xmusicpartner.py`** (aliased as `xmusicpart` / `partition_to_musicxml.py`):
  Engraves deterministic, vendor-neutral W3C MusicXML 3.1/4.0 scores from any partition, importing seamlessly into MuseScore, Dorico, Sibelius, or GNU LilyPond:
  ```bash
  python3 hexdec/tools/xmusicpartner.py -p "/0279/18AF/35CE/46BD/" -o score.musicxml --score-type multi
  ```

* **`generate_monomer_midi.py`**:
  Batch-synthesizes the entire 14-monomer rhythm catalogue in `hexdec/midi/`.

---

## 5. Mathematical Core Library

### `mosaic_sorting.py`
The shared Python library implementing the canonical 5-tier natural sorting cascade:
1. **Tier 1**: Dihedral Orbit Size $\vert\mathcal{O}\vert \in \{1, 2, 4, 8, 16, 32\}$ (ascending).
2. **Tier 2**: Symmetric Block Count $s \in \{4, 3, 2, 1, 0\}$ (descending; blue-to-pink gradient).
3. **Tier 3**: Chord Dispersion Energy $E(P)$ (descending; regular to clustered).
4. **Tier 4**: Canonical Stride Profile Multiset (unoriented cyclic stride tuples).
5. **Tier 5**: Canonical Lexicographic Tie-Breaker.

Provides foundational helpers: `get_mosaic_sort_key()`, `is_block_symmetric()`, `compute_mosaic_chord_energy()`, `get_chirality_signature()`, and `format_partition_slash()`.

---

## 6. Small Universes Algebraic Auditing

* **`verify_small_universes.py`**:
  Rigorous combinatorial and fixed-point verification of $D\_4$ ($z\_2^2$ on $\mathbb{Z}\_4$, 2 monomers) and $D\_9$ ($z\_3^3$ on $\mathbb{Z}\_9$, 1 monomer, 8 trimers = 25 comosaics):
  ```bash
  python3 hexdec/tools/verify_small_universes.py --universe all
  ```

* **`d9_tiered_census.py`**:
  Calculates the exact 5-tier natural sorting cascade for the 8 trimers of $\mathbb{Z}\_9$.

---

## 7. Monograph Quality Assurance Tools

* **`audit_british_spelling.py`**:
  Enforces British English spelling conventions across all LaTeX monograph chapters (`realisable`, `factorisation`, `characterisation`, `stabiliser`, `behaviour`, `catalogue`):
  ```bash
  python3 hexdec/tools/audit_british_spelling.py hexdec/sec
  ```

* **`audit_display_math.py`**:
  Audits all TeX files to ensure no standalone display math environments (such as `equation`, `align`, or `\[...\]`) end with trailing terminal punctuation bacilli (`.` or `,`):
  ```bash
  python3 hexdec/tools/audit_display_math.py hexdec/sec
  ```
