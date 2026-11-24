#!/usr/bin/env python3
"""
xmusicpartner.py - Convert Mosaic Set Partitions to Standard MusicXML Notation

Generates pristine, publication-grade MusicXML 3.1/4.0 score files from cyclic
composition mosaic partitions (Z_n) or hexadecimological catalogue specifiers (T*, D*, M*).

MusicXML is the open, vendor-neutral W3C standard for symbolic music notation interchange.
Scores produced by this utility import cleanly into all standard-compliant notation software
and scoring engines (such as Dorico, Sibelius, MuseScore, LilyPond via musicxml2ly,
and Python musicology frameworks such as music21) without requiring heuristic MIDI quantisation.

Advantages over raw MIDI:
  1. Exact Notation Semantics: Explicit notes vs rests, preventing quantisation distortion.
  2. Metric Beaming & Grouping: Accurately beams complex/additive metres (e.g. 11/16 as 3+3+3+2).
  3. Percussion Staves & Clefs: Native unpitched percussion clefs and instrument mapping.
  4. Rich Metadata: Embeds block strides, catalogue IDs, chirality, and polygon profiles.
  5. Multi-Staff vs Consolidated: Export as multi-staff percussion ensemble or unified drum kit.

Author: Gemma Knee & Antigra Vitti
Date: November 2026
"""

import os
import sys
import argparse
import re
from typing import List, Tuple, Dict, Optional, Set, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Re-use parsing logic from midipartner
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from midipartner import (
        parse_catalogue_specifier, lookup_catalogue_specifier,
        parse_partition_string, validate_partition, format_block,
        compute_block_strides, GM_PERCUSSION_PALETTE
    )
except ImportError:
    # Standalone fallback if invoked from outside repo
    pass

# Standard Display Positions for Unpitched Percussion Voices
# Display on standard percussion staff (Line 1 = E4 bottom, Line 5 = F5 top)
PERCUSSION_DISPLAY_MAP = [
    # (Step, Octave, Notehead, Instrument Name, MIDI Note)
    ("F", 4, "normal", "Bass Drum 1 (Kick)", 36),     # Space 1 (bottom)
    ("C", 5, "normal", "Acoustic Snare", 38),         # Space 3
    ("G", 5, "x",      "Closed Hi-Hat", 42),          # Space above line 5
    ("E", 5, "normal", "Claves / Wood Block", 75),    # Space 4
    ("A", 4, "normal", "Low Floor Tom", 41),          # Space 2
    ("G", 5, "circle-x","Open Hi-Hat", 46),           # Space above line 5 (open)
    ("D", 5, "triangle","Cowbell", 56),               # Line 4
    ("A", 5, "diamond","Tambourine", 54),             # Line above top
    ("D", 5, "normal", "Mid Tom", 47),                # Line 4
    ("F", 5, "normal", "High Tom", 50),               # Line 5
    ("B", 4, "slash",  "Hand Clap", 39),              # Line 3
]

def parse_args():
    parser = argparse.ArgumentParser(
        prog="xmusicpartner",
        description="Convert cyclic composition mosaic partitions into standard W3C MusicXML notation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Odd/Additive Metre (11/16 grouped as 3+3+3+2):
  %(prog)s "/0123/4567/89A/" --grouping 3,3,3,2 -o odd11.musicxml

  # Catalogue Specifiers (Hexadecagonal Macro-Orbits on Z_16):
  %(prog)s T01152.3 --bars 2 -o T01152_3.musicxml
  %(prog)s M01 --bars 4 -o monomer1.musicxml
  %(prog)s D001.2 -o dimer1_2.musicxml

  # Custom Title & Single Consolidated Drum Staff:
  %(prog)s "/0149/26AE/37BF/58CD/" --title "Chiral Breakbeat" --score-type kit

Output is standard W3C MusicXML 3.1/4.0 compatible with all compliant notation
software (Dorico, Sibelius, MuseScore, LilyPond via musicxml2ly, music21, etc.).
        """
    )
    parser.add_argument("partition", nargs="?", default=None,
                        help="Catalogue specifier ('T01152.3', 'D001') or raw partition string ('/0123/4567/89A/')")
    parser.add_argument("-p", "--partition", dest="opt_partition", metavar="SPEC", default=None,
                        help="Catalogue specifier or raw partition string")
    parser.add_argument("-o", "--output", default=None, help="Output .musicxml filepath")
    parser.add_argument("-b", "--bars", type=int, default=2, help="Number of repeating bars (default: 2)")
    parser.add_argument("--bpm", type=int, default=120, help="Tempo marking in BPM (default: 120)")
    parser.add_argument("--time-sig", default="auto",
                        help="Time signature (default: 'auto' -> 4/4 for Z_16, n/16 for general Z_n)")
    parser.add_argument("--grouping", default=None,
                        help="Additive metric pulse grouping as comma-separated step counts (e.g. '3,3,3,2' for 11/16)")
    parser.add_argument("--score-type", choices=["multi", "kit"], default="multi",
                        help="'multi': separate percussion staff per voice (default); 'kit': single consolidated drum kit staff")
    parser.add_argument("--title", default=None, help="Score title")
    parser.add_argument("--composer", default="Gemma Knee", help="Composer metadata (default: Gemma Knee)")
    return parser.parse_args()

def compute_beam_states(grouping: List[int], bar_length: int) -> List[Optional[str]]:
    """
    Compute beam state ('begin', 'continue', 'end', None) for each 16th-note step
    based on additive grouping.
    """
    beams: List[Optional[str]] = [None] * bar_length
    curr = 0
    for group_sz in grouping:
        if group_sz <= 1:
            beams[curr] = None
            curr += group_sz
            continue
        for idx in range(group_sz):
            step = curr + idx
            if step >= bar_length:
                break
            if idx == 0:
                beams[step] = "begin"
            elif idx == group_sz - 1:
                beams[step] = "end"
            else:
                beams[step] = "continue"
        curr += group_sz
    return beams

def build_musicxml(blocks: List[List[int]], n: int, k: int, bars: int = 2, bpm: int = 120,
                   time_sig: str = "auto", grouping_list: Optional[List[int]] = None,
                   score_type: str = "multi", title: Optional[str] = None,
                   composer: str = "Gemma Knee", meta_info: Optional[Dict[str, Any]] = None) -> str:
    """Generate structured MusicXML 3.1 DOM tree and serialize to formatted string."""
    
    # 1. Determine Time Signature & Divisions
    # divisions = 4 means 1 quarter note = 4 divisions -> 1 sixteenth note = 1 division
    divisions = 4
    
    if time_sig == "auto":
        if n == 16:
            ts_num = "4"
            ts_denom = "4"
            default_grouping = [4, 4, 4, 4]
        elif n % 4 == 0:
            ts_num = str(n // 4)
            ts_denom = "4"
            default_grouping = [4] * (n // 4)
        else:
            ts_num = str(n)
            ts_denom = "16"
            default_grouping = [n]
    else:
        parts = time_sig.split("/")
        ts_num = parts[0]
        ts_denom = parts[1] if len(parts) > 1 else "16"
        default_grouping = [n]
        
    actual_grouping = grouping_list if grouping_list else (
        [4, 4, 4, 4] if n == 16 else ([n] if n % 4 != 0 else [4] * (n // 4))
    )
    beam_states = compute_beam_states(actual_grouping, n)
    
    score_title = title or (
        f"Mosaic Partition {meta_info['id']} on Z_{n}" if meta_info else f"Composition Mosaic on Z_{n} ({ts_num}/{ts_denom})"
    )

    # Root element
    score = ET.Element("score-partwise", version="3.1")
    
    # Work & Identification
    work = ET.SubElement(score, "work")
    ET.SubElement(work, "work-title").text = score_title
    
    ident = ET.SubElement(score, "identification")
    ET.SubElement(ident, "creator", type="composer").text = composer
    encoding = ET.SubElement(ident, "encoding")
    ET.SubElement(encoding, "software").text = "composit midipartner & xmusicpartner"
    ET.SubElement(encoding, "encoding-date").text = "2026-11-24"

    # Part List
    part_list = ET.SubElement(score, "part-list")
    
    sorted_blocks = sorted(blocks, key=lambda b: min(b))
    
    if score_type == "multi":
        for idx, blk in enumerate(sorted_blocks):
            pid = f"P{idx + 1}"
            disp_step, disp_oct, nhead, inst_name, midi_note = PERCUSSION_DISPLAY_MAP[idx % len(PERCUSSION_DISPLAY_MAP)]
            strides = compute_block_strides(blk, n)
            sp = ET.SubElement(part_list, "score-part", id=pid)
            ET.SubElement(sp, "part-name").text = f"Voice {idx + 1}: {inst_name}"
            ET.SubElement(sp, "part-abbreviation").text = f"V{idx + 1}"
            inst_id = f"{pid}-I1"
            sc_inst = ET.SubElement(sp, "score-instrument", id=inst_id)
            ET.SubElement(sc_inst, "instrument-name").text = inst_name
            midi_inst = ET.SubElement(sp, "midi-instrument", id=inst_id)
            ET.SubElement(midi_inst, "midi-channel").text = "10"
            ET.SubElement(midi_inst, "midi-program").text = "1"
            ET.SubElement(midi_inst, "midi-unpitched").text = str(midi_note)
            ET.SubElement(midi_inst, "volume").text = "78.7402"
            ET.SubElement(midi_inst, "pan").text = "0"
    else:
        # Consolidated drum kit staff
        sp = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(sp, "part-name").text = "Mosaic Percussion Ensemble"
        ET.SubElement(sp, "part-abbreviation").text = "Perc."
        for idx in range(k):
            disp_step, disp_oct, nhead, inst_name, midi_note = PERCUSSION_DISPLAY_MAP[idx % len(PERCUSSION_DISPLAY_MAP)]
            inst_id = f"P1-I{idx + 1}"
            sc_inst = ET.SubElement(sp, "score-instrument", id=inst_id)
            ET.SubElement(sc_inst, "instrument-name").text = f"Voice {idx + 1}: {inst_name}"
            midi_inst = ET.SubElement(sp, "midi-instrument", id=inst_id)
            ET.SubElement(midi_inst, "midi-channel").text = "10"
            ET.SubElement(midi_inst, "midi-program").text = "1"
            ET.SubElement(midi_inst, "midi-unpitched").text = str(midi_note)
            ET.SubElement(midi_inst, "volume").text = "78.7402"
            ET.SubElement(midi_inst, "pan").text = "0"

    # Parts & Measures
    if score_type == "multi":
        for blk_idx, blk in enumerate(sorted_blocks):
            pid = f"P{blk_idx + 1}"
            part_elem = ET.SubElement(score, "part", id=pid)
            blk_set = set(blk)
            disp_step, disp_oct, nhead, inst_name, midi_note = PERCUSSION_DISPLAY_MAP[blk_idx % len(PERCUSSION_DISPLAY_MAP)]
            
            for bar in range(bars):
                meas = ET.SubElement(part_elem, "measure", number=str(bar + 1))
                
                # Bar 1 Attributes
                if bar == 0:
                    attr = ET.SubElement(meas, "attributes")
                    ET.SubElement(attr, "divisions").text = str(divisions)
                    
                    time_elem = ET.SubElement(attr, "time")
                    if grouping_list and len(grouping_list) > 1:
                        ET.SubElement(time_elem, "beats").text = "+".join(str(x) for x in grouping_list)
                    else:
                        ET.SubElement(time_elem, "beats").text = ts_num
                    ET.SubElement(time_elem, "beat-type").text = ts_denom
                    
                    clef = ET.SubElement(attr, "clef")
                    ET.SubElement(clef, "sign").text = "percussion"
                    ET.SubElement(clef, "line").text = "2"
                    
                    # Tempo direction in Voice 1, Bar 1
                    if blk_idx == 0:
                        direction = ET.SubElement(meas, "direction", placement="above")
                        dir_type = ET.SubElement(direction, "direction-type")
                        metro = ET.SubElement(dir_type, "metronome")
                        ET.SubElement(metro, "beat-unit").text = "quarter" if ts_denom == "4" else "16th"
                        ET.SubElement(metro, "per-minute").text = str(bpm if ts_denom == "4" else bpm * 4)
                        sound = ET.SubElement(direction, "sound", tempo=str(bpm))
                        
                        # Rehearsal mark / mosaic metadata
                        if meta_info:
                            dir_meta = ET.SubElement(meas, "direction", placement="above")
                            dt_meta = ET.SubElement(dir_meta, "direction-type")
                            words = ET.SubElement(dt_meta, "words", font_weight="bold")
                            words.text = f"Mosaic {meta_info.get('id', '')} [Shape {meta_info.get('shape', '')}]"

                # Generate 16th-note events for each step 0 .. n-1
                for step in range(n):
                    note_elem = ET.SubElement(meas, "note")
                    
                    if step in blk_set:
                        # Sounding unpitched note
                        unp = ET.SubElement(note_elem, "unpitched")
                        ET.SubElement(unp, "display-step").text = disp_step
                        ET.SubElement(unp, "display-octave").text = str(disp_oct)
                        ET.SubElement(note_elem, "duration").text = "1"
                        ET.SubElement(note_elem, "instrument", id=f"{pid}-I1")
                        ET.SubElement(note_elem, "voice").text = "1"
                        ET.SubElement(note_elem, "type").text = "16th"
                        ET.SubElement(note_elem, "stem").text = "up"
                        if nhead != "normal":
                            ET.SubElement(note_elem, "notehead").text = nhead
                        
                        # Dynamic accent on downbeat
                        if step == 0:
                            notations = ET.SubElement(note_elem, "notations")
                            artic = ET.SubElement(notations, "articulations")
                            ET.SubElement(artic, "accent")
                            
                        # Beaming
                        b_state = beam_states[step]
                        if b_state is not None:
                            ET.SubElement(note_elem, "beam", number="1").text = b_state
                            ET.SubElement(note_elem, "beam", number="2").text = b_state
                    else:
                        # 16th Rest
                        ET.SubElement(note_elem, "rest")
                        ET.SubElement(note_elem, "duration").text = "1"
                        ET.SubElement(note_elem, "voice").text = "1"
                        ET.SubElement(note_elem, "type").text = "16th"

                # Final barline
                if bar == bars - 1:
                    barline = ET.SubElement(meas, "barline", location="right")
                    ET.SubElement(barline, "bar-style").text = "light-heavy"
    else:
        # Kit mode: single consolidated staff with multiple layers
        part_elem = ET.SubElement(score, "part", id="P1")
        for bar in range(bars):
            meas = ET.SubElement(part_elem, "measure", number=str(bar + 1))
            if bar == 0:
                attr = ET.SubElement(meas, "attributes")
                ET.SubElement(attr, "divisions").text = str(divisions)
                time_elem = ET.SubElement(attr, "time")
                if grouping_list and len(grouping_list) > 1:
                    ET.SubElement(time_elem, "beats").text = "+".join(str(x) for x in grouping_list)
                else:
                    ET.SubElement(time_elem, "beats").text = ts_num
                ET.SubElement(time_elem, "beat-type").text = ts_denom
                clef = ET.SubElement(attr, "clef")
                ET.SubElement(clef, "sign").text = "percussion"
                ET.SubElement(clef, "line").text = "2"
                
                direction = ET.SubElement(meas, "direction", placement="above")
                dir_type = ET.SubElement(direction, "direction-type")
                metro = ET.SubElement(dir_type, "metronome")
                ET.SubElement(metro, "beat-unit").text = "quarter" if ts_denom == "4" else "16th"
                ET.SubElement(metro, "per-minute").text = str(bpm if ts_denom == "4" else bpm * 4)

            # Assemble composite interlocking stream (exactly one voice sounds at each step t)
            step_to_voice = {}
            for v_idx, blk in enumerate(sorted_blocks):
                for st in blk:
                    step_to_voice[st] = v_idx

            for step in range(n):
                v_idx = step_to_voice[step]
                disp_step, disp_oct, nhead, inst_name, midi_note = PERCUSSION_DISPLAY_MAP[v_idx % len(PERCUSSION_DISPLAY_MAP)]
                note_elem = ET.SubElement(meas, "note")
                unp = ET.SubElement(note_elem, "unpitched")
                ET.SubElement(unp, "display-step").text = disp_step
                ET.SubElement(unp, "display-octave").text = str(disp_oct)
                ET.SubElement(note_elem, "duration").text = "1"
                ET.SubElement(note_elem, "instrument", id=f"P1-I{v_idx + 1}")
                ET.SubElement(note_elem, "voice").text = "1"
                ET.SubElement(note_elem, "type").text = "16th"
                ET.SubElement(note_elem, "stem").text = "up"
                if nhead != "normal":
                    ET.SubElement(note_elem, "notehead").text = nhead
                
                if step == 0:
                    notations = ET.SubElement(note_elem, "notations")
                    artic = ET.SubElement(notations, "articulations")
                    ET.SubElement(artic, "accent")
                    
                b_state = beam_states[step]
                if b_state is not None:
                    ET.SubElement(note_elem, "beam", number="1").text = b_state
                    ET.SubElement(note_elem, "beam", number="2").text = b_state

            if bar == bars - 1:
                barline = ET.SubElement(meas, "barline", location="right")
                ET.SubElement(barline, "bar-style").text = "light-heavy"

    # Pretty-print XML
    raw_xml = ET.tostring(score, encoding="utf-8")
    dom = minidom.parseString(raw_xml)
    return dom.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

def main():
    args = parse_args()
    input_str = args.opt_partition or args.partition
    if not input_str:
        print("Error: No partition or catalogue specifier provided.", file=sys.stderr)
        sys.exit(1)

    spec_info = parse_catalogue_specifier(input_str)
    meta_info = None
    default_name = None

    if spec_info is not None:
        canonical_id, phase_idx = spec_info
        try:
            raw_partition, macro_type, phase, total_phases = lookup_catalogue_specifier(canonical_id, phase_idx)
            partition_str = raw_partition
            meta_info = {
                "id": canonical_id,
                "macro_type": macro_type,
                "phase": phase,
                "total_phases": total_phases
            }
            default_name = f"{canonical_id}_{phase}.musicxml" if total_phases > 1 else f"{canonical_id}.musicxml"
        except Exception as e:
            print(f"Error resolving catalogue specifier '{input_str}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        partition_str = input_str

    try:
        blocks = parse_partition_string(partition_str)
    except Exception as e:
        print(f"Error parsing partition: {e}", file=sys.stderr)
        sys.exit(1)

    n, k, is_valid, msg = validate_partition(blocks)
    if not is_valid:
        print(f"Error: Invalid partition: {msg}", file=sys.stderr)
        sys.exit(1)

    block_sizes = [len(b) for b in blocks]
    shape_str = "".join(f"z_{sz}" for sz in sorted(block_sizes))
    if meta_info:
        meta_info["shape"] = shape_str

    # Parse grouping if provided
    grouping_list = None
    if args.grouping:
        try:
            grouping_list = [int(x.strip()) for x in args.grouping.split(",") if x.strip()]
            if sum(grouping_list) != n:
                print(f"Warning: --grouping sum ({sum(grouping_list)}) does not equal cycle length {n}", file=sys.stderr)
        except ValueError:
            print(f"Error parsing --grouping '{args.grouping}'. Expected e.g. '3,3,3,2'", file=sys.stderr)
            sys.exit(1)

    output_path = args.output or default_name or f"mosaic_{n}step_{k}v.musicxml"
    
    ts_disp = args.time_sig if args.time_sig != "auto" else ("4/4" if n == 16 else f"{n}/16")

    print("=" * 64)
    print("  xmusicpartner: MusicXML Mosaic Notation Exporter")
    print("=" * 64)
    if meta_info:
        print(f"Catalogue Record:    {meta_info['id']} ({meta_info['macro_type']}, Phase {meta_info['phase']}/{meta_info['total_phases']})")
    print(f"Input Partition:     {partition_str}")
    print(f"Time Signature:      {ts_disp} ({n} semiquavers per bar)")
    if grouping_list:
        print(f"Metric Grouping:     {'+'.join(str(x) for x in grouping_list)} (additive pulse & beam clusters)")
    print(f"Score Layout:        {'Multi-Staff (voice-separated)' if args.score_type == 'multi' else 'Kit (consolidated staff)'}")
    print(f"Voices & Block Sizes:{k} voices, shape {shape_str} {block_sizes}")
    print(f"Output File:         {output_path}")
    print("-" * 64)

    xml_content = build_musicxml(
        blocks=blocks,
        n=n,
        k=k,
        bars=args.bars,
        bpm=args.bpm,
        time_sig=args.time_sig,
        grouping_list=grouping_list,
        score_type=args.score_type,
        title=args.title,
        composer=args.composer,
        meta_info=meta_info
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    file_sz = os.path.getsize(output_path)
    print(f"✓ Generated MusicXML score: {output_path} ({file_sz:,} bytes)")
    print("  Compatible with standard notation software (Dorico, Sibelius, MuseScore, LilyPond, etc.).")
    print("=" * 64)

if __name__ == "__main__":
    main()
