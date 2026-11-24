# Composition Mosaics Dihedral Orbit Dataset (`mosaics`)

This dataset provides the complete, authoritative census and combinatorial classification of all **509** non-equivalent dihedral composition mosaics (set partitions up to rotation and reflection) across circular rings $\mathbb{Z}\_1$ through $\mathbb{Z}\_8$ under the physical symmetries of the dihedral groups $D\_n$.

Accompanying monograph: *An Atlas of Composition Mosaics: The Complete Dihedral Universe from* $\mathbb{Z}\_1$ *to* $\mathbb{Z}\_8$ *(Gemma Knee & Antigra Vitti, November 2026).*

---

## 1. Files in this Directory

* [`mosaics.tsv`](mosaics.tsv): Tab-delimited master catalogue of all 509 dihedral composition mosaics (510 lines including header, RFC/GitHub Flat Data compliant).
* [`mosaics.csv`](mosaics.csv): Comma-separated values master table.
* [`mosaics.json`](mosaics.json): Structured JSON array of all 509 mosaic record objects.
* [`mosaic_blocks.tsv`](mosaic_blocks.tsv): Tab-delimited relational table of all 1,983 constituent blocks across all 509 mosaics, linking directly into `polyatlas` (1,984 lines including header).
* [`mosaic_blocks.csv`](mosaic_blocks.csv): Comma-separated values block relational table.
* [`mosaic_blocks.json`](mosaic_blocks.json): Structured JSON array of all 1,983 block record objects.

---

## 2. Orbit Census Summary ($\mathbb{Z}\_1$ to $\mathbb{Z}\_8$)

| Ring $\mathbb{Z}\_n$ | $\lvert D\_n \rvert$ | Bell Partitions $B\_n$ | Shapes | Dihedral Mosaics | Orbit Size Decomposition $\sum a\_k \omega^k$ |
| :---: | :---: | :---: | :---: | :---: | :--- |
| $\mathbb{Z}\_1$ | 1 | 1 | 1 | **1** | $1\omega^1$ |
| $\mathbb{Z}\_2$ | 2 | 2 | 2 | **2** | $2\omega^1$ |
| $\mathbb{Z}\_3$ | 6 | 5 | 3 | **3** | $2\omega^1 + 1\omega^3$ |
| $\mathbb{Z}\_4$ | 8 | 15 | 5 | **7** | $3\omega^1 + 2\omega^2 + 2\omega^4$ |
| $\mathbb{Z}\_5$ | 10 | 52 | 7 | **12** | $2\omega^1 + 10\omega^5$ |
| $\mathbb{Z}\_6$ | 12 | 203 | 11 | **37** | $4\omega^1 + 3\omega^2 + 6\omega^3 + 12\omega^6 + 12\omega^{12}$ |
| $\mathbb{Z}\_7$ | 14 | 877 | 15 | **93** | $3\omega^1 + 28\omega^7 + 62\omega^{14}$ |
| $\mathbb{Z}\_8$ | 16 | 4,140 | 22 | **354** | $4\omega^1 + 6\omega^2 + 27\omega^4 + 132\omega^8 + 185\omega^{16}$ |
| **Total** | --- | **5,295** | **66** | **509** | OEIS sequence A084708 |

---

## 3. Record Schema: Master Mosaic Catalogue (`mosaics`)

| Field | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | `382` | Global integer index ($1 \dots 509$) spanning the octonary universe. |
| `n` | Integer | `8` | Cyclic ring order $n \in \{1, \dots, 8\}$. |
| `local_id` | Integer | `227` | Local integer index within ring $\mathbb{Z}\_n$ ($1 \dots M\_n$). |
| `shape` | String | `(2,2,2,2)` | Integer partition shape $\lambda \vdash n$ in descending order. |
| `slash` | String | `/01/25/37/46/` | Canonical partition representation in hexadecimal slash notation. |
| `orbit_size` | Integer | `16` | Dihedral orbit length $\lvert \mathcal{O} \rvert \in \{1, \dots, \lvert D\_n \rvert\}$ under the action of $D\_n$. |
| `stab_size` | Integer | `1` | Stabiliser subgroup order $\lvert D\_n \rvert / \lvert \mathcal{O} \rvert$. |
| `s_count` | Integer | `4` | Number of bilaterally symmetric (achiral) constituent blocks. |
| `chirality` | String | `ssss` | Chirality signature string recording achiral (`s`) and chiral (`c`) blocks. |
| `energy` | Integer | `30` | Circular chord dispersion energy $E(\mathcal{M})$. |
| `poly_profile` | String | `2-1+2-2+2-3+2-4` | Multi-set of constituent `polyatlas` polygon classes. |
| `manifest` | String | `2-1@0+:17/...` | Full relational embedding manifest linking blocks into `polyatlas`. |

---

## 4. Record Schema: Relational Block Bridge (`mosaic_blocks`)

| Field | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `global_mosaic_id` | Integer | `382` | Parent mosaic global identifier ($1 \dots 509$). |
| `n` | Integer | `8` | Cyclic ring order $n \in \{1, \dots, 8\}$. |
| `local_mosaic_id` | Integer | `227` | Parent mosaic local index within ring $\mathbb{Z}\_n$ ($1 \dots M\_n$). |
| `block_idx` | Integer | `2` | 1-based index of block within the canonical partition ($1 \dots s$). |
| `vertices` | String | `25` | Hexadecimal vertex string of block $B$ in circular order. |
| `size` | Integer | `2` | Block cardinality $d = \lvert B \rvert$. |
| `poly_class` | String | `2-3` | Canonical polygon class identifier $k\text{-}i$ in `polyatlas` for ring $n$. |
| `canon_comp` | String | `35` | Canonical circular stride composition of polygon class in `polyatlas`. |
| `realised_comp` | String | `35` | Realised forward cyclic stride composition along block perimeter. |
| `root` | Integer | `2` | Spatial root vertex $v\_0 = \min(B) \in \mathbb{Z}\_n$. |
| `chirality` | String | `+` | Chirality orientation: `+` (direct cyclic translation) vs `-` (retrograde / flipped). |

---

## 5. The Block Manifest Syntax

Every constituent block embedding is encoded by a compact manifest token:
```text
[Class]@[Root][Chirality]:[Realised Strides]
```
where:
* **Class**: The canonical polygon class identifier $k\text{-}i$ in `polyatlas` (e.g. `3-3` for the chiral triangle on $\mathbb{Z}\_6$).
* **Root**: The starting vertex $v\_0 = \min(B) \in \mathbb{Z}\_n$.
* **Chirality**: Orientation sign relative to canonical form (`+` for direct rotational translation, `-` for retrograde / flipped).
* **Realised Strides**: The forward cyclic strides along the perimeter of block $B$ starting from $v\_0$.

For example, in Mosaic `33` on $\mathbb{Z}\_6$ (`/013/245/`), the manifest is `3-3@0+:123/3-3@2-:213`, showing that the two chiral scalene triangles partition the hexagon as an enantiomorphic direct-and-reflected pair. In Mosaic `382` on $\mathbb{Z}\_8$ (`/01/25/37/46/`), the four chords realise the cyclic Skolem sequence spanning distances 1, 2, 3, 4 through classes `2-1`, `2-2`, `2-3`, and `2-4`.
