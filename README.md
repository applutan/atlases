# Atlases of Cyclic Composition Mosaics

A collection of comprehensive cartographic monographs, algebraic classifications, and discrete geometry atlases exploring cyclic lattices, polygon orbits, and uniform composition mosaics on $\mathbb{Z}\_n$.

## Volumes

1. **`polyatlas/` — The Polygonal Burnsidean**
   * *An Atlas of Inscribed Polygons from* $\mathbb{Z}\_1$ *to* $\mathbb{Z}\_{16}$ (113 pages).
   * Complete algebraic classification of all dihedral orbits of inscribed single polygons, evaluated via the Cauchy--Frobenius bracelet generating polynomial $CF\_n(x)$ alongside cyclic necklace polynomials $N\_n(x)$.
   * Includes 19-column generating function coefficient tables ($n=1 \dots 16$), machine-readable polygon manifests (`inngons.tsv`, `inngons.csv`, `inngons.json`), and circular stride classification.

2. **`hexdec/` — Hexadecality: The Atlas of Hexadecagonal Compositions**
   * *Affine Macro-Orbits and Galois Multiplier Symmetries on* $\mathbb{Z}\_{16}$ (255 pages).
   * Exhaustive cartography of **uniform composition mosaics**—set partitions where every block possesses identical cardinality ($z\_k^m$, with $n = k \cdot m$). Explores the square-dimension uniform universes where $k = m = \sqrt{n}$: $\mathbb{Z}\_4$ ($z\_2^2$, 2 monomers), $\mathbb{Z}\_9$ ($z\_3^3$, 25 comosaics across 9 macro-orbits), and $\mathbb{Z}\_{16}$ ($z\_4^4$, $83{,}488$ dihedral comosaics in $21{,}030$ affine macro-orbits).
   * Full visual cartouches, Galois dilation cycles ($\mu\_3, \mu\_7, \mu\_5$), dihedral stabilizer classifications, chord dispersion energies, relational polygon bridges into `polyatlas`, and an interlocking percussion suite (`midipartner` for MIDI and `xmusicpartner` for W3C MusicXML score engraving).
