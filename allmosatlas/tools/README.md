# Allmosatlas Tooling Suite

Command-line utilities for computing, verifying, and generating the multi-lattice composition mosaic datasets, analytical tables, and visual plates for *An Atlas of Composition Mosaics* ($\mathbb{Z}\_1$ through $\mathbb{Z}\_8$).

All routines are fully parameterised via `argparse` with built-in `--help` documentation.

---

## Tool Directory

| Script | Purpose | Key Arguments |
| :--- | :--- | :--- |
| `generate_multilattice_atlas.py` | Primary multi-lattice generator: computes all 509 mosaics, emits summary tables, and compiles 10-page TikZ visual plates. | `--max-n 8`, `--output-dir allmosatlas` |
| `generate_multilattice_relational_data.py` | Bridges mosaics to `polyatlas` polygon classes; emits normalised TSV, CSV, JSON datasets with bijectivity verification. | `--inngons-tsv <path>`, `--data-dir <path>`, `--verify` |
| `compute_mosaic_census_z1_z8.py` | Fast census engine computing partition numbers, shape stratifications, and dihedral orbit counts across $\mathbb{Z}\_1..\mathbb{Z}\_8$. | `--max-n 8` |
| `investigate_cyclic_vs_dihedral_ordering.py` | Comparative analysis between dihedral ($D\_8$) and cyclic ($C\_8$) orbit orderings and chiral pair proximities. | `--verbose`, `--output <file>` |

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
