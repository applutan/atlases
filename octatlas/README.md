# An Atlas of Composition Mosaics: The Complete Dihedral Universe from $\mathbb{Z}\_1$ to $\mathbb{Z}\_8$

**Volume 3 of the Coffee-Table Trilogy on Circular Lattice Combinatorics**

*Gemma Knee & Antigra Vitti* (November 2026)

---

## Overview

This monograph provides the complete visual atlas, algebraic classification, and relational database of composition mosaics (set partitions of cyclic lattices up to rotation and reflection) across the circular rings $\mathbb{Z}\_1$ through $\mathbb{Z}\_8$.

Across the eight rings, the first eight Bell numbers generate exactly **5,295** set partitions. Under the physical symmetries of the respective dihedral groups $D\_n$, these partitions gather into exactly **509** non-equivalent dihedral composition mosaics, realising the initial terms of sequence **OEIS A084708**:

$$
\sum_{n=1}^8 M_n = 1 + 2 + 3 + 7 + 12 + 37 + 93 + 354 = 509
$$

## Key Structural Highlights

* **Visual Cartography**: Ten vector plates displaying all 509 configurations in pure geometric form as shaded convex polygons, metric chords, and singleton pips.
* **Block Symmetry & Chirality**: Bilateral symmetry colouring distinguishes achiral blocks (blue) from chiral scalene blocks (rose pink). Block chirality first emerges on the hexagonal lattice $\mathbb{Z}\_6$ with the scalene triangle of strides $(1, 2, 3)$.
* **Singleton Shattering Duality**: Functorial bijection preserving bivariate orbit polynomials $Q_\lambda(\omega)$ under replacement of parts $a \to 1^a$.
* **The Cyclic Skolem Structure on** $\mathbb{Z}\_8$: Orbit 227 of $\mathbb{Z}\_8$ realises the unique cyclic Skolem difference sequence of order 4 on four chords covering distances 1, 2, 3, 4, seeding the affine macro-orbits on the double-cover hexadecagon $\mathbb{Z}\_{16}$.
* **Normalised Relational Data**: Every block across all 509 mosaics is linked directly into the canonical inscribed polygon census of *The Polygonal Burnsidean* (`polyatlas`) via self-contained manifest descriptors.

## Directory Structure

* [`octatlas.pdf`](octatlas.pdf): The complete compiled monograph (24 pages, A4).
* [`data/`](data/): Master datasets (`mosaics.tsv`, `mosaics.csv`, `mosaics.json`) and relational block tables (`mosaic_blocks.tsv`, `mosaic_blocks.csv`, `mosaic_blocks.json`).
* [`plates/`](plates/): Standalone TikZ visual plates source (`plates_z1_z8.tex`) and compiled vector booklet (`plates_z1_z8.pdf`, 10 pages).
* [`sec/`](sec/): Monograph text chapters (`Preface.tex`, `LatticeArchitecture.tex`, `CanonicalTaxonomy.tex`, `VisualAtlas.tex`).
* [`tools/`](tools/): Persistent command-line generation and verification utilities with built-in `--help`.
