# Allmosatlas Tooling Suite

Command-line utilities and high-performance OpenMP C++ solvers for computing, verifying, and generating multi-lattice composition mosaic datasets, analytical tables, and visual plates for *An Atlas of Composition Mosaics* ($\mathbb{Z}\_1$ through $\mathbb{Z}\_{16}$).

All Python routines are fully parameterised via `argparse` with built-in `--help` documentation; C++ solvers leverage OpenMP multithreading for ultra-fast generation across large combinatorial state spaces.

---

## Tool Directory

### High-Performance C++ Solvers
| Tool | Purpose | Performance / Scope |
| :--- | :--- | :--- |
| `generate_extended_shape_census.cpp` | OpenMP parallel backtrack solver evaluating dihedral orbit polynomials $Q\_\lambda(\omega)$ for all 271 partition shapes across $\mathbb{Z}\_1..\mathbb{Z}\_{12}$. Emits LaTeX tables for Chapter 2. | ~3.0s for all 271 shapes ($\mathbb{Z}\_1..\mathbb{Z}\_{12}$) |
| `generate_extended_relational_data.cpp` | OpenMP parallel relational generator emitting `mosaics.tsv`/`.csv` (219,467 records) and `mosaic_blocks.tsv`/`.csv` (1,202,459 block embeddings) with `polyatlas` linkage. | ~6.7s for full dataset |
| `solve_z16_exact.cpp` | Specialised symmetry backtrack solver determining reflection and half-turn rotation counts for $\mathbb{Z}\_{16}$, yielding the exact dihedral count $M\_{16} = 327{,}731{,}950$. | 0.52s execution |
| `compute_shape_census.cpp` | Dedicated shape-by-shape orbit counter for individual ring orders. | Fast verification engine |

### Python Generation & Verification Utilities
| Script | Purpose | Key Arguments |
| :--- | :--- | :--- |
| `generate_z9_plates.py` | Generator for the standalone 23-page TikZ vector booklet for the 1,350 mosaics of $\mathbb{Z}\_9$ (`plates_z9.pdf`). | `--output-dir <path>` |
| `generate_multilattice_atlas.py` | Primary multi-lattice generator: computes mosaics, emits summary tables, and compiles TikZ visual plates for $\mathbb{Z}\_1..\mathbb{Z}\_8$. | `--max-n 8`, `--output-dir allmosatlas` |
| `generate_multilattice_relational_data.py` | Python relational bridge into `polyatlas` polygon classes with bidirectional integrity verification. | `--inngons-tsv <path>`, `--data-dir <path>`, `--verify` |
| `compute_mosaic_census_z1_z8.py` | Fast census engine computing partition numbers, shape stratifications, and dihedral orbit counts across $\mathbb{Z}\_1..\mathbb{Z}\_8$. | `--max-n 8` |
| `investigate_cyclic_vs_dihedral_ordering.py` | Comparative analysis between dihedral ($D\_8$) and cyclic ($C\_8$) orbit orderings and chiral pair proximities. | `--verbose`, `--output <file>` |
| `../../tools/verify_against_appendix_b3.py` | Automated cross-verification audit checking Table 1.1 and Table 2.1 directly against *Mosaicality* Appendix B.3 across all 12 rings and 271 shapes. | `--verbose` |

---

## Usage Examples

### 1. Generating Master Datasets and Visual Plates

To compute all 509 dihedral composition mosaics and build both the LaTeX tables and TikZ visual plates:
```bash
python3 allmosatlas/tools/generate_multilattice_atlas.py --max-n 8 --output-dir allmosatlas
```

### 2. Generating Machine-Readable Relational Data

To generate the normalized TSV, CSV, and JSON datasets linking all constituent blocks directly into `polyatlas`:
```bash
python3 allmosatlas/tools/generate_multilattice_relational_data.py \
    --inngons-tsv polyatlas/data/inngons.tsv \
    --data-dir allmosatlas/data \
    --verify
```

### 3. Rapid Census Verification

To verify the OEIS A084708 sequence counts from $\mathbb{Z}\_1$ to $\mathbb{Z}\_8$:
```bash
python3 allmosatlas/tools/compute_mosaic_census_z1_z8.py --max-n 8
```
