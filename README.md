# Atlases of Cyclic Composition Mosaics

A collection of comprehensive cartographic monographs, algebraic classifications, and discrete geometry atlases exploring cyclic lattices, polygon orbits, and uniform composition mosaics on $\mathbb{Z}\_n$.

## Volumes

1. **`polyatlas/` — The Polygonal Burnsidean**
   * *An Atlas of Inscribed Polygons from* $\mathbb{Z}\_1$ *to* $\mathbb{Z}\_{16}$ (113 pages).
   * Complete algebraic classification of all dihedral orbits of inscribed single polygons, evaluated via the Cauchy--Frobenius bracelet generating polynomial $CF\_n(x)$ alongside cyclic necklace polynomials $N\_n(x)$.
   * Includes 19-column generating function coefficient tables ($n=1 \dots 16$), machine-readable polygon manifests (`inngons.tsv`, `inngons.csv`), and circular stride classification.

2. **`unimosatlas/` — Hexadecality: The Atlas of Hexadecagonal Compositions**
   * *Affine Macro-Orbits and Galois Multiplier Symmetries on* $\mathbb{Z}\_{16}$ (252 pages).
   * Exhaustive cartography of **uniform composition mosaics**—set partitions where every block possesses identical cardinality ($z\_k^m$, with $n = k \cdot m$). Explores the square-dimension uniform universes where $k = m = \sqrt{n}$: $\mathbb{Z}\_4$ ($z\_2^2$, 2 monomers), $\mathbb{Z}\_9$ ($z\_3^3$, 25 comosaics across 9 macro-orbits), and $\mathbb{Z}\_{16}$ ($z\_4^4$, $83{,}488$ dihedral comosaics in $21{,}030$ affine macro-orbits).
   * Full visual cartouches, Galois dilation cycles ($\mu\_3, \mu\_7, \mu\_5$), dihedral stabiliser classifications, chord dispersion energies, relational polygon bridges into `polyatlas`, and an interlocking percussion suite (`midipartner` for MIDI and `xmusicpartner` for W3C MusicXML score engraving, documented in [`tools/PERCUSSION_SUITE.md`](tools/PERCUSSION_SUITE.md)).

3. **`allmosatlas/` — An Atlas of Composition Mosaics**
   * *The Complete Dihedral Universe from* $\mathbb{Z}\_1$ *to* $\mathbb{Z}\_9$ (58 pages).
   * Exhaustive combinatorial census, algebraic classification, and visual cartography of all **1,859** non-equivalent dihedral composition mosaics across 26,442 set partitions (governed by Bell numbers $B\_1 \dots B\_9$, realising OEIS sequence A084708).
   * 33 high-density vector plates (10 plates for $\mathbb{Z}\_1..\mathbb{Z}\_8$ and 23 plates for $\mathbb{Z}\_9$) displaying all 1,859 pure shaded geometric tilings, generalising cyclic lattice combinatorics, Faà di Bruno multinomial shape stratification, Singleton Shattering Duality, bilateral block symmetries and the emergence of chirality at $\mathbb{Z}\_6$.
   * Comprehensive tabular censuses encompassing all 914 partition shapes and $382{,}030{,}946$ mosaics across $\mathbb{Z}\_1..\mathbb{Z}\_{16}$, detailed shape inventory for $\mathbb{Z}\_1..\mathbb{Z}\_{12}$ across 271 shapes, and machine-readable relational datasets (`mosaics.tsv`, `mosaic_blocks.tsv`) containing 219,467 mosaics and 1,202,459 block embeddings bridging directly into `polyatlas`.
