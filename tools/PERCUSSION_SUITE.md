# A Polyrhythmic Percussion Suite & Score Engraving Engine

A comprehensive guide and reference manual for translating cyclic composition mosaics into multi-track polyrhythmic percussion loops (General MIDI) and notation-ready scores (W3C MusicXML).

The underlying command-line tools—[`midipartner.py`](midipartner.py) and [`xmusicpartner.py`](xmusicpartner.py)—are cross-cutting engines located in `tools/`. They operate universally across all cyclic lattices $\mathbb{Z}\_n$ and set partition shapes (both uniform and non-uniform).

---

## 1. Acoustic Architecture: The Interlocking Hocket

The geometric partition of $n$ circular vertices $\mathbb{Z}\_n = \{0, 1, \dots, n-1\}$ into $s$ disjoint blocks:

$$\mathcal{M} = \{B_1, B_2, \dots, B_s\} \quad \text{where} \quad \bigcup_{j=1}^s B_j = \mathbb{Z}_n, \quad B_j \cap B_k = \emptyset$$

admits an immediate acoustic realisation as an $n\text{-step}$ rhythmic measure (with semiquaver / sixteenth-note step resolution).

Because $\mathcal{M}$ forms a true set partition of the cyclic grid:
* At every time step $t \in \{0, \dots, n-1\}$, **exactly one** block $B\_j$ contains $t$.
* When each block is assigned a distinct percussive voice, the voices **never collide or sound simultaneously**.
* They generate an interlocking **hocket**: an uninterrupted stream of pulses where rhythmic and melodic counterpoint emerges purely from timbral variation.

---

## 2. Standard Voice & Timbre Assignment

For standard four-block partitions (such as the uniform comosaics of $\mathbb{Z}\_{16}$ or four-part mosaics on $\mathbb{Z}\_8$), synthesis defaults to General MIDI Channel 10:

| Voice Index | Grid Criterion | Instrument | MIDI Note | Pitch-Class Staff Position |
| :---: | :--- | :--- | :---: | :--- |
| **Voice 0** | Block containing downbeat vertex $0$ | Bass Drum 1 (Kick) | 36 | Space 1 ($F_4$) |
| **Voice 1** | Lowest remaining vertex in block | Acoustic Snare | 38 | Space 3 ($C_5$) |
| **Voice 2** | Lowest remaining vertex in block | Closed Hi-Hat | 42 | Above Line 5 with $\times$ noteheads ($G_5$) |
| **Voice 3** | Lowest remaining vertex in block | Claves | 75 | Space 4 ($E_5$) |

For partitions with fewer than 4 blocks, higher voices remain unallocated; for partitions with $s > 4$ blocks, additional auxiliary percussion instruments (Side Stick 37, Low Floor Tom 41, Open Hi-Hat 46, Crash Cymbal 49, Ride Cymbal 51) are allocated sequentially.

---

## 3. Metric Symmetries of the Hexadecagonal Monomers

The 14 canonical monomers of $\mathbb{Z}\_{16}$ ($M\_1 \dots M\_{14}$) exhibit distinct groove personalities governed by their dihedral and affine stabilisers:

* **Regular Pulse ($M\_1$, Four-on-the-Floor)**:
  Consists of the four cosets of $4\mathbb{Z}\_{16}$. Each instrument plays an isochronous stream of four quarter notes, offset by single sixteenth notes, sounding as four interwoven pulses.
* **Palindromic Funk Grooves ($M\_2, M\_3, M\_4$)**:
  Order-8 dihedral stabilisers induce exact half-measure translational symmetry ($t \mapsto t + 8$) and bilateral retrogrades. The kick and snare form balanced, syncopated funk phrases with predictable metric counterpoint.
* **Reflectional Syncopations ($M\_5, M\_6, M\_7, M\_8$)**:
  $M\_8$ exhibits an inversion groove ($t \mapsto t + 8$), swapping instrument pairings halfway through the bar. $M\_5, M\_6, M\_7$ possess metric retrograde axes where the sixteenth-note pattern reads identically forwards and backwards around specific beats.
* **Chiral Breakbeats ($M\_9 \dots M\_{14}$)**:
  Lacking Euclidean symmetries, these rhythms sound completely irregular and unpredictable in linear time. Their hidden periodicity only reveals itself under affine multiplier decimation: sub-sampling the rhythm at every third sixteenth note ($\mu\_3 \colon t \mapsto 3t \pmod{16}$) recovers the exact original rhythmic profile.

Pre-synthesised General MIDI loops for all 14 monomers are housed in `unimosatlas/midi/monomer1.mid` through `monomere.mid`.

---

## 4. `midipartner.py` — MIDI Synthesis Engine

Synthesises any valid mosaic partition into a multi-track General MIDI percussion loop on Channel 10.

### Catalogue Specifier Resolution
`midipartner` parses catalogue specifiers across the $21{,}030$ affine macro-orbits ($83{,}488$ dihedral comosaics) of *Hexadecality*:
```bash
# Synthesize Phase 3 of Tetramer T01152 at 63 BPM for 8 bars
python3 tools/midipartner.py T01152.3 --output T01152_3.mid --bpm 63 --bars 8

# Synthesize Dimer D001 (Phase 2)
python3 tools/midipartner.py D001.2 --bpm 90 --bars 4

# Synthesize Monomer M01
python3 tools/midipartner.py M01 --bpm 110 --bars 4
```

### Arbitrary Partitions & Odd Metres ($n \le 36$)
Beyond precomputed lookups, `midipartner` accepts arbitrary partition strings:
```bash
# Explicit slash notation on Z_16
python3 tools/midipartner.py "/0149/26AE/37BF/58CD/" -o chiral_breakbeat.mid

# 11-step partition on Z_11 (automatically embedded as 11/16 metre)
python3 tools/midipartner.py "/0123/4567/89A/" -o odd_11_16.mid

# Nonagonal trimer on Z_9 (9/16 metre)
python3 tools/midipartner.py "/012/345/678/" --bpm 108 -o trimer_z9.mid

# Non-uniform mosaic on Z_8 (from allmosatlas)
python3 tools/midipartner.py "/01/25/37/46/" --bpm 120 -o skolem_z8.mid
```

### Additive Metre Groupings & Dynamic Accents
For odd metres, `midipartner` supports custom sub-beat groupings via `--grouping` and explicit acoustic accents via `--accents`:
```bash
# Balkan 11/16 with 3+3+3+2 additive pulse grouping
python3 tools/midipartner.py "/0123/4567/89A/" --grouping 3,3,3,2 -o balkan_11_16.mid

# Custom acoustic accents on beats 0, 3, 6, 9
python3 tools/midipartner.py "/0123/4567/89A/" --time-sig 11/16 --accents 0,3,6,9 -o accented.mid
```

### Voice Muting & Solo Audition
To facilitate subtractive acoustic analysis or isolate specific polyrhythmic strata:
```bash
# Mute Voice 1 (Kick) to audition accompanying percussion strata
python3 tools/midipartner.py T01152.3 --silent 1 -o no_kick.mid

# Mute Voices 1 and 3 simultaneously
python3 tools/midipartner.py T01152.3 --mute 1 3 -o hihat_snare_only.mid
```

---

## 5. `xmusicpartner.py` — W3C MusicXML Score Engraving

While Standard MIDI files provide instantaneous audio playback, raw MIDI lacks musical notation semantics: it contains no concept of rests, metric beam groupings, unpitched percussion staves, or score typography. 

The `xmusicpartner` engine translates cyclic composition mosaics directly into strict, schema-compliant **W3C MusicXML 3.1** percussion scores.

### Key Engraving Features
* **Native Unpitched Percussion Clefs**: Emits standard unpitched clef definitions (`<clef><sign>percussion</sign></clef>`) mapping voices to Space 1 (Kick), Space 3 (Snare), Space 4 (Claves), and above Line 5 with cross noteheads (Hi-Hat).
* **Automated Metric Beam Grouping**: Correctly beams sixteenth notes according to standard music typography ($4+4+4+4$ in $4/4$, $3+3+3+2$ in $11/16$, etc.), converting inter-hocket silences into rigorous musical rests.
* **Score Typologies**:
  * **Multi-Staff Ensemble (`--score-type multi`, default)**: Assigns each polygon block to an independent percussion staff, clearly exhibiting the individual polyrhythmic stride of each part.
  * **Consolidated Drum Kit (`--score-type single`)**: Collapses all voices onto a single 5-line percussion staff with upward/downward voice stem splitting for performance by a single drum kit player.

### Usage Examples
```bash
# Multi-staff percussion ensemble score
python3 tools/xmusicpartner.py -p "/0279/18AF/35CE/46BD/" -o score_ensemble.musicxml --score-type multi

# Consolidated drum kit score
python3 tools/xmusicpartner.py -p "/0279/18AF/35CE/46BD/" -o score_kit.musicxml --score-type single

# Catalog lookup notation export
python3 tools/xmusicpartner.py T01152.3 -o tetramer_notation.musicxml
```

The resulting `.musicxml` files import natively into **MuseScore**, **Finale**, **Sibelius**, or **LilyPond** (`musicxml2ly`) with zero manual rest alignment or quantisation correction required.
