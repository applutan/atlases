# Hexadecality Composition Mosaics & Relational Datasets

This directory provides the complete, authoritative relational datasets, affine macro-orbit directories, and polygon embedding manifests for the composition mosaics of *Hexadecality*. The data spans equal-block partitions across three circular metric universes:

* $\mathbb{Z}\_4$ ($z\_2^2$ universe, 2 monomer orbits)
* $\mathbb{Z}\_9$ ($z\_3^3$ universe, 1 monomer, 8 trimers = 25 dihedral comosaics)
* $\mathbb{Z}\_{16}$ ($z\_4^4$ universe, 14 monomers, 295 dimers, 20,721 tetramers = 83,488 dihedral comosaics in 21,030 affine macro-orbits)

Accompanying monograph: *Hexadecality: The Atlas of Hexadecagonal Compositions* (Gemma Knee & Antigra Vitti, November 2026).

---

## 1. Files in this Directory

### Master Registries and Concordances
* [`z16_macro_mosaics.tsv`](z16_macro_mosaics.tsv): The 21,030 canonical affine macro-orbit representatives on $\mathbb{Z}\_{16}$ (Phase 1 primary representatives selected via the 5-tier natural sorting cascade).
* [`z16_macro_mosaic_blocks.tsv`](z16_macro_mosaic_blocks.tsv): Relational block decompositions for all 84,120 constituent 4-vertex blocks across the primary macro-orbits, linking each block directly to its parent polygon class in [`polyatlas`](../../polyatlas/data/inngons.tsv).
* [`z16_mosaics.tsv`](z16_mosaics.tsv): Exhaustive dihedral census of all 83,488 comosaics across all 4 Galois dilation phases ($\mu\_1 = \mathrm{id}, \mu\_3, \mu\_7, \mu\_5$).
* [`z16_mosaic_blocks.tsv`](z16_mosaic_blocks.tsv): Full relational block decomposition for all 333,952 block records across all 83,488 dihedral comosaics.
* [`hexadecality_index.txt`](hexadecality_index.txt): Master plate concordance indexing all 21,030 macro-orbits to their exact plate and grid coordinates in the 252-page monograph.
* [`tetramers_full_index.txt`](tetramers_full_index.txt): Full 20,721-tetramer catalogue sorted via the 5-tier natural sorting cascade.
* [`doublets.json`](doublets.json): Structured JSON array of mutually orthogonal partition doublets on $\mathbb{Z}\_{16}$.

### Small Universes
* [`z4_mosaics.tsv`](z4_mosaics.tsv): Complete catalogue for the $z\_2^2$ universe on $\mathbb{Z}\_4$ (2 orbits).
* [`z4_mosaic_blocks.tsv`](z4_mosaic_blocks.tsv): Relational block bridge for $\mathbb{Z}\_4$ (4 block records).
* [`z9_mosaics.tsv`](z9_mosaics.tsv): Complete catalogue for the $z\_3^3$ universe on $\mathbb{Z}\_9$ (25 comosaics across 9 macro-orbits).
* [`z9_mosaic_blocks.tsv`](z9_mosaic_blocks.tsv): Relational block bridge for $\mathbb{Z}\_9$ (75 block records).

---

## 2. Record Schemas & Field Definitions

### Mosaics Catalogue Schema (`z*_mosaics.tsv`, `z16_macro_mosaics.tsv`)

| Column | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `orbit_id` | string | `T00646` | Canonical identifier for the dihedral comosaic orbit. Prefixed by oligomer type (`M` for monomer, `D` for dimer, `T` for tetramer). |
| `macro_id` | string | `T00646` | Identifier of the parent affine macro-orbit under Galois multiplication by $\langle \mu\_3 \rangle$. |
| `oligomer_type` | string | `Tetramer` | Macro-orbit cycle length under $\mu\_3$: `Monomer` (period 1), `Dimer` (period 2), `Trimer` (period 3), or `Tetramer` (period 4). |
| `phase` | integer | `1` | Dilation phase index within the macro-orbit ($1 \le \text{phase} \le 4$). Phase 1 is the primary canonical representative. |
| `dilation_mult`| integer | `1` | Galois multiplier corresponding to the current phase ($\mu\_1 = 1$, $\mu\_2 = 3$, $\mu\_3 = 7$, $\mu\_4 = 5$). |
| `is_primary` | integer | `1` | Primary representative flag: `1` if this comosaic is the leading representative selected by the sorting cascade; `0` otherwise. |
| `orbit_size` | integer | `32` | Size of the dihedral orbit $\vert\mathcal{O}\vert \in \{1, 4, 16, 32\}$ under the physical action of $D\_{16}$. |
| `stab_size` | integer | `1` | Order of the stabilizer subgroup $\vert\mathrm{Stab}\vert = 32 / \vert\mathcal{O}\vert$. |
| `s_sym` | integer | `4` | Number of constituent blocks possessing internal bilateral reflection symmetry ($0 \le s \le 4$). |
| `energy` | integer | `544` | Total chord dispersion energy $E(P)$, defined as the sum of squared intra-block circular chord lengths. |
| `chirality_sig`| string | `[ssss]` | 4-character block chirality signature: `s` (symmetric / achiral) or `n` (non-symmetric / chiral). |
| `partition` | string | `/0189/23AB/45CD/67EF/` | Set partition in hexadecimal slash notation. |
| `poly_profile` | string | `4x4-12` | Formal multiset composition profile of constituent polygon classes defined in `polyatlas`. |
| `block_manifest`| string | `4-12@0+:1717/...` | Slash-delimited composite manifest linking every block to its geometric embedding. |

### Relational Blocks Bridge Schema (`z*_mosaic_blocks.tsv`, `z16_macro_mosaic_blocks.tsv`)

| Column | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `orbit_id` | string | `T00646` | Identifier of the parent comosaic orbit. |
| `macro_id` | string | `T00646` | Identifier of the parent affine macro-orbit. |
| `phase` | integer | `1` | Dilation phase index ($1 \dots 4$). |
| `dilation_mult`| integer | `1` | Galois multiplier $\mu\_m \in \{1, 3, 7, 5\}$. |
| `is_primary` | integer | `1` | Primary representative flag (`1` or `0`). |
| `block_idx` | integer | `1` | 1-based index of the block within the partition ($1 \le j \le 4$). |
| `vertices` | string | `0 1 8 9` | Space-separated list of lattice vertex indices in hexadecimal notation. |
| `poly_class` | string | `4-12` | Canonical inscribed polygon class designation $k\text{-}i$ in `polyatlas`. |
| `canon_comp` | string | `1717` | Canonical circular stride composition word from `polyatlas`. |
| `realised_comp`| string | `1717` | Forward perimeter stride sequence realised from the root vertex. |
| `root` | string | `0` | Root lattice vertex $v\_0 = \min(B\_j)$ in hexadecimal. |
| `chirality` | string | `+` | Rotational orientation sign: `+` for direct cyclic stride alignment; `-` for retrograde reflection. |
| `manifest_token`| string | `4-12@0+:1717` | Exact embedding descriptor token $\mathrm{[Class]}@\mathrm{[Root]}[\mathrm{Sign}]:\mathrm{[Strides]}$. |

---

## 3. Mathematical Invariants & Manifest Syntax

### Stabilizer Order and Orbit Size
By the orbit-stabilizer theorem under the dihedral action $D\_n$:

$$\vert\mathrm{Stab}\vert = \frac{2n}{\vert\mathcal{O}\vert}$$

On $\mathbb{Z}\_{16}$, the dihedral group has order $\vert D\_{16}\vert = 32$. The possible orbit sizes are $\vert\mathcal{O}\vert \in \{1, 4, 16, 32\}$, corresponding to stabilizer orders $\vert\mathrm{Stab}\vert \in \{32, 8, 2, 1\}$.

### Chord Dispersion Energy $E(P)$
The chord dispersion energy of an equal-block partition $P = \{B\_1, \dots, B\_m\}$ on circular ring $\mathbb{Z}\_n$ is the sum of squared chord metrics across all intra-block vertex pairs:

$$E(P) = \sum\_{j=1}^m \sum\_{\{u, v\} \subset B\_j} \mathrm{dist}\_{\mathbb{Z}\_n}(u, v)^2$$

where $\mathrm{dist}\_{\mathbb{Z}\_n}(u, v) = \min(\vert u - v\vert, n - \vert u - v\vert)$ denotes the shortest cyclic perimeter distance.

### Embedding Manifest Token
Each constituent block is uniquely resolved into its `polyatlas` counterpart via the canonical token:

$$\mathrm{[Class]}@\mathrm{[Root]}[\mathrm{Sign}]:\mathrm{[RealisedStrides]}$$

* **Class**: The parent polygon orbit $k\text{-}i$ defined in `polyatlas/data/inngons.csv`.
* **Root**: The root lattice coordinate $v\_0 = \min(B\_j) \in \{0, \dots, n-1\}$.
* **Sign**: Orientation flag (`+` if the realised perimeter strides match the forward clockwise order; `-` if retrograde reflection is required).
* **Realised Strides**: The forward cyclic stride sequence $c\_1 c\_2 \dots c\_k$ connecting successive vertices starting from $v\_0$.

---

## 4. Census Summary Across Metric Universes

| Metric Universe | Ring $\mathbb{Z}\_n$ | Partition Shape $z\_k^m$ | Monomers | Dimers | Trimers | Tetramers | Dihedral Comosaics | Total Blocks | Macro-Orbits |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $D\_4$ | $\mathbb{Z}\_4$ | $z\_2^2$ | 2 | 0 | 0 | 0 | **2** | 4 | **2** |
| $D\_9$ | $\mathbb{Z}\_9$ | $z\_3^3$ | 1 | 0 | 8 | 0 | **25** | 75 | **9** |
| $D\_{16}$ | $\mathbb{Z}\_{16}$ | $z\_4^4$ | 14 | 295 | 0 | 20,721 | **83,488** | 333,952 | **21,030** |

---

## 5. Query Cookbook & Verification Recipes

### Count macro-orbits by oligomer cycle length
```bash
awk -F'\t' 'NR>1 {count[$3]++} END {for (t in count) print t ": " count[t]}' unimosatlas/data/z16_macro_mosaics.tsv
```

### Find all maximally symmetric comosaics ($\vert\mathrm{Stab}\vert = 32$)
```bash
awk -F'\t' '$8 == 32 {print $1, $3, $9, $10, $12}' unimosatlas/data/z16_macro_mosaics.tsv
```

### Extract all purely achiral comosaics with four symmetric blocks (`[ssss]`)
```bash
awk -F'\t' '$11 == "[ssss]" {count++} END {print "Total [ssss] comosaics: " count}' unimosatlas/data/z16_macro_mosaics.tsv
```

### Identify the highest chord energy comosaic
```bash
awk -F'\t' 'NR>1 {if ($10 > max) {max = $10; line = $0}} END {print "Max energy " max ": " line}' unimosatlas/data/z16_macro_mosaics.tsv
```

### Inspect the relational block manifest for a specific macro-orbit (e.g. `T00646`)
```bash
grep -E '^T00646\b' unimosatlas/data/z16_macro_mosaic_blocks.tsv
```

### Cross-reference a mosaic block to `polyatlas` polygon data
```bash
awk -F',' '$3 == 16 && $2 == "4-12"' polyatlas/data/inngons.csv
```
