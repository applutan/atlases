# An Atlas of Composition Mosaics: The Complete Dihedral Universe from $\mathbb{Z}\_1$ to $\mathbb{Z}\_9$

**Volume 3 of the Coffee-Table Trilogy on Circular Lattice Combinatorics**

*Gemma Knee & Antigra Vitti* (November 2026)

---

## Overview

This monograph provides the complete visual atlas, algebraic classification, and relational database of composition mosaics (set partitions of cyclic lattices up to rotation and reflection) across the circular rings $\mathbb{Z}\_1$ through $\mathbb{Z}\_9$, alongside extended analytical censuses reaching to $\mathbb{Z}\_{16}$.

Across the first nine rings, the Bell numbers generate exactly **26,442** set partitions. Under the physical symmetries of the respective dihedral groups $D\_n$, these partitions gather into exactly **1,859** non-equivalent dihedral composition mosaics, realising the initial terms of sequence **OEIS A084708**:

$$
\sum_{n=1}^9 M_n = 1 + 2 + 3 + 7 + 12 + 37 + 93 + 354 + 1{,}350 = 1{,}859
$$

Extended computational censuses in Chapter 1 and Chapter 2 encompass all 914 partition shapes and **382,030,946** mosaics through $\mathbb{Z}\_{16}$, with complete shape-by-shape inventories across all 271 partition shapes for $\mathbb{Z}\_1..\mathbb{Z}\_{12}$.

## Key Structural Highlights

* **Visual Cartography**: 33 high-density vector plates displaying all 1,859 configurations in pure geometric form as shaded convex polygons, metric chords, and singleton pips (10 plates for $\mathbb{Z}\_1..\mathbb{Z}\_8$ and 23 plates for $\mathbb{Z}\_9$).
* **Block Symmetry & Chirality**: Bilateral symmetry colouring distinguishes achiral blocks (blue) from chiral scalene blocks (rose pink). Block chirality first emerges on the hexagonal lattice $\mathbb{Z}\_6$ with the scalene triangle of strides $(1, 2, 3)$.
* **Singleton Shattering Duality**: Functorial bijection preserving bivariate orbit polynomials $Q_\lambda(\omega)$ under replacement of parts $a \to 1^a$.
* **The Cyclic Skolem Structure on** $\mathbb{Z}\_8$: Orbit 227 of $\mathbb{Z}\_8$ realises the unique cyclic Skolem difference sequence of order 4 on four chords covering distances 1, 2, 3, 4, seeding the affine macro-orbits on the double-cover hexadecagon $\mathbb{Z}\_{16}$.
* **Normalised Relational Data**: Every block across all 219,467 mosaics up to $\mathbb{Z}\_{12}$ is linked directly into the canonical inscribed polygon census of *The Polygonal Burnsidean* (`polyatlas`) via self-contained manifest descriptors.

## Directory Structure

* [`allmosatlas.pdf`](allmosatlas.pdf): The complete compiled monograph (58 pages, A4).
* [`data/`](data/): Master datasets (`mosaics.tsv`, `mosaics.csv`) and relational block tables (`mosaic_blocks.tsv`, `mosaic_blocks.csv`) covering 219,467 mosaics and 1,202,459 block embeddings.
* [`plates/`](plates/): Standalone TikZ visual plates source (`plates_z1_z8.tex`, `plates_z9.tex`) and compiled vector booklets (`plates_z1_z8.pdf` [10 pages], `plates_z9.pdf` [23 pages]).
* [`sec/`](sec/): Monograph text chapters (`Preface.tex`, `LatticeArchitecture.tex`, `CanonicalTaxonomy.tex`, `VisualAtlas.tex`).
* [`gen/`](gen/): Extended census tables (`census_summary_z1_z16.tex`, `shape_census_z1_z12.tex`).
* [`tools/`](tools/): Persistent command-line generation and verification utilities with built-in `--help`.
