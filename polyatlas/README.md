# The Polygonal Burnsidean: An Atlas of Inscribed Polygons from $\mathbb{Z}\_1$ to $\mathbb{Z}\_{16}$

**Volume 1 of the Coffee-Table Trilogy on Circular Lattice Combinatorics**

*Gemma Knee & Antigra Vitti* (November 2026)

---

## Overview

This directory houses the algebraic classification, visual cartography, and relational database of single inscribed polygons on circular lattices $\mathbb{Z}\_1$ through $\mathbb{Z}\_{16}$ under the physical action of the dihedral groups $D\_n$.

The monograph **`polyatlas.pdf`** (113 pages) provides an exhaustive cartography classifying all **5,099** non-equivalent dihedral orbits of single inscribed polygons across $\mathbb{Z}\_1..\mathbb{Z}\_{16}$ (and all 9,033 cyclic orbits):
* **Polynomial Theory**: Evaluates the Cauchy--Frobenius bracelet generating polynomials $CF\_n(x)$ alongside cyclic necklace polynomials $N\_n(x)$.
* **Visual Atlas Plates**: High-density vector plates illustrating all 5,099 orbits on circular clockfaces (with vertex 0 at 12 o'clock, increasing clockwise).
* **Colour Taxonomy**: Achiral polygons with bilateral reflection symmetry are highlighted in **mosaical blue**; chiral enantiomorphic twin pairs (which split under cyclic rotation $C\_n$) are highlighted in **rose pink**.
* **Circular Stride Compositions**: Every polygon is catalogued by its canonical circular perimeter stride word $\mathbf{s} = (s_1, \dots, s_k)$ with $\sum s_i = n$.

---

## 1. Machine-Readable Datasets (`data/`)

* [`data/inngons.tsv`](data/inngons.tsv) / [`data/inngons.csv`](data/inngons.csv): Authoritative census of all 5,099 dihedral orbits across $\mathbb{Z}\_1..\mathbb{Z}\_{16}$, recording canonical compositions, local class IDs (`k-i`), vertex subsets in hexadecimal slash notation, orbit lengths, and chirality flags.

---

## 2. Tooling Suite (`tools/`)

* [`tools/generate_poly_atlas_v2.py`](tools/generate_poly_atlas_v2.py): Vector TikZ plates generator implementing the standard clockface angular layout ($\theta_v = 90^\circ - v \cdot \frac{360^\circ}{n}$).
