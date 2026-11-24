# Inscribed Polygons Dihedral Orbit Dataset (`inngons`)

This dataset provides the complete, authoritative census and combinatorial classification of all **5,099** non-equivalent single inscribed polygons across the circular rings $\mathbb{Z}\_1$ through $\mathbb{Z}\_{16}$ under the physical symmetries of the dihedral group $D\_n$.

Accompanying monograph: *The Polygonal Burnsidean: An Atlas of Inscribed Polygons from* $\mathbb{Z}\_1$ *to* $\mathbb{Z}\_{16}$ (Gemma Knee & Antigra Vitti, November 2026).

---

## 1. Files in this Directory

* [`inngons.csv`](inngons.csv): RFC 4180 comma-separated values table (5,100 lines including header).
* [`inngons.tsv`](inngons.tsv): Tab-delimited table with comment metadata.
* [`inngons.json`](inngons.json): Structured JSON array of record objects.

---

## 2. Record Schema & Field Descriptions

| Column | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `composition` | string | `24334` | Canonical circular stride composition word $c\_1 c\_2 \dots c\_k$ connecting successive vertices along the perimeter. Sum of parts $\sum c\_i = n$; length $= k$. Set to `---` for the empty polygon ($k=0$). |
| `class_id` | string | `5-20` | Local atlas designation $k\text{-}i$, denoting the $i\text{-th}$ non-equivalent $k\text{-gon}$ orbit on lattice $\mathbb{Z}\_n$. |
| `n` | integer | `16` | Size of the ambient cyclic lattice $\mathbb{Z}\_n$ ($1 \le n \le 16$). |
| `k` | integer | `5` | Cardinality of the polygon ($0 \le k \le n$). |
| `subset` | string | `/0269C/` | Canonical vertex subset representative in hexadecimal slash notation. |
| `orbit_size` | integer | `16` | Length of the orbit $\vert\mathcal{O}\vert \in \{1, 2, \dots, 2n\}$ under the action of $D\_n$. |
| `is_achiral` | integer | `1` | Bilateral reflection symmetry flag: `1` if bilaterally symmetric (achiral under $D\_n$); `0` if chiral enantiomorph (splits into two orbits under cyclic rotation $C\_n$). |

### Stabilizer Invariant

The stabilizer subgroup size is uniquely determined by the orbit-stabilizer theorem:

$$\vert\mathrm{Stab}\vert = \frac{2n}{\vert\mathcal{O}\vert}$$

### Hexadecimal Encoding
For lattice vertices $v \ge 10$, hexadecimal digits are employed:
`A` $= 10$, `B` $= 11$, `C` $= 12$, `D` $= 13$, `E` $= 14$, `F` $= 15$.

---

## 3. Orbit Census Summary ($\mathbb{Z}\_1$ to $\mathbb{Z}\_{16}$)

| Ring $\mathbb{Z}\_n$ | $2^n$ Subsets | $\vert D\_n\vert$ | Dihedral Orbits | Cyclic Orbits | Chiral Pairs | Chiral % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $\mathbb{Z}\_{1}$ | 2 | 2 | **2** | 2 | 0 | 0.0% |
| $\mathbb{Z}\_{2}$ | 4 | 4 | **3** | 3 | 0 | 0.0% |
| $\mathbb{Z}\_{3}$ | 8 | 6 | **4** | 4 | 0 | 0.0% |
| $\mathbb{Z}\_{4}$ | 16 | 8 | **6** | 6 | 0 | 0.0% |
| $\mathbb{Z}\_{5}$ | 32 | 10 | **8** | 8 | 0 | 0.0% |
| $\mathbb{Z}\_{6}$ | 64 | 12 | **13** | 14 | 1 | 7.7% |
| $\mathbb{Z}\_{7}$ | 128 | 14 | **18** | 20 | 2 | 11.1% |
| $\mathbb{Z}\_{8}$ | 256 | 16 | **30** | 36 | 6 | 20.0% |
| $\mathbb{Z}\_{9}$ | 512 | 18 | **46** | 60 | 14 | 30.4% |
| $\mathbb{Z}\_{10}$ | 1,024 | 20 | **78** | 108 | 30 | 38.5% |
| $\mathbb{Z}\_{11}$ | 2,048 | 22 | **126** | 188 | 62 | 49.2% |
| $\mathbb{Z}\_{12}$ | 4,096 | 24 | **224** | 352 | 128 | 57.1% |
| $\mathbb{Z}\_{13}$ | 8,192 | 26 | **380** | 632 | 252 | 66.3% |
| $\mathbb{Z}\_{14}$ | 16,384 | 28 | **687** | 1,182 | 495 | 72.1% |
| $\mathbb{Z}\_{15}$ | 32,768 | 30 | **1,224** | 2,192 | 968 | 79.1% |
| $\mathbb{Z}\_{16}$ | 65,536 | 32 | **2,250** | 4,116 | 1,866 | 82.9% |
| **Total** | --- | --- | **5,099** | **9,033** | **3,934** | --- |

---

## 4. Example Query One-Liners

### Count orbits per ring
```bash
awk -F',' 'NR>1 {count[$3]++} END {for (n in count) print "Z_" n ": " count[n]}' polyatlas/data/inngons.csv | sort -V
```

### Extract 16-step African and Afro-Cuban clave rhythms
```bash
grep -E '^(24334|23344|23434|23443|33334)' polyatlas/data/inngons.csv
```

### Find all maximally symmetric orbits ($\vert\mathcal{O}\vert = 1$)
```bash
awk -F',' '$6 == 1 {print $1, $2, "Z_" $3, $5}' polyatlas/data/inngons.csv
```

### Filter all heptatonic scales on $\mathbb{Z}\_{12}$ (Forte 7-X set classes)
```bash
awk -F',' '$3 == 12 && $4 == 7 {print $1, $2, $5, ($7==1 ? "achiral" : "chiral")}' polyatlas/data/inngons.csv
```
