#!/usr/bin/env python3
"""
midipartner.py - Convert Mosaic Set Partitions and Catalogue Macro-Orbits into Multi-Voice Percussion MIDI

Primary Hexadecimological Interface:
  Accepts catalogue specifiers for all 21,030 affine macro-orbits on Z_16:
    T01152.3   -> Tetramer T01152, Phase 3 (of 4)
    T01152     -> Tetramer T01152, Phase 1 (default canonical representative)
    D001.2     -> Dimer D001, Phase 2 (of 2)
    M01        -> Monomer M01 (Phase 1)

Extended Functionality:
  Accepts arbitrary set partitions of Z_n (for any n <= 36 using Base-36 digits 0-9, A-Z, or
  arbitrary n using hyphenated/spaced integers) in flexible notation:
    /0149/26AE/37BF/58CD/
    0149,26AE,37BF,58CD
    /0/1D/245/37F/689BE/AC/
    /012/345/678/
    /0-1-15-35/2-3-16-34/.../

Features:
  1. Instant resolution of all 83,488 dihedral orbits across 21,030 macro-orbits.
  2. Automatically deduces cycle length n (semiquavers per bar) and k (parts/voices).
  3. Supports Base-36 characters (0-9: 0..9, A-Z/a-z: 10..35) for n up to 36.
  4. Supports silent/rest parts: nominate any part from 1 to k (or voice 0 to k-1)
     as silent/unvoiced via --silent / --mute or -i silent / 0.
  5. Assigns well-contrasted General MIDI percussion instruments on Channel 10.
  6. Assembles an interlocking, non-overlapping multi-bar rhythmic loop.

Author: Gemma Knee
"""

import sys
import os
import struct
import argparse
import re
from typing import List, Tuple, Set, Dict, Optional

# Standard General MIDI Drum Map (Channel 10)
# Curated palette of acoustically distinct, non-melodic percussive voices
GM_PERCUSSION_PALETTE = [
    (36, "Bass Drum 1 (Kick)",   "Sub/low thump"),
    (38, "Acoustic Snare",       "Mid crack/snap"),
    (42, "Closed Hi-Hat",        "High metallic tick"),
    (75, "Claves",               "Piercing high wood knock"),
    (37, "Side Stick",           "Tight acoustic rim click"),
    (41, "Low Floor Tom",        "Deep resonant body"),
    (46, "Open Hi-Hat",          "Sustained high sizzle"),
    (76, "High Wood Block",      "Bright hollow wood"),
    (56, "Cowbell",              "Dry metallic clang"),
    (47, "Low-Mid Tom",          "Mid-low tom resonance"),
    (54, "Tambourine",           "Jingle/shake burst"),
    (39, "Hand Clap",            "Mid snappy slap"),
    (69, "Cabasa",               "Metallic friction scrape"),
    (50, "High Tom",             "High-frequency tom punch"),
    (70, "Maracas",              "Crisp high grain rattle"),
    (77, "Low Wood Block",       "Warm low wood hollow"),
    (58, "Vibraslap",            "Rattling teeth effect"),
    (67, "High Agogo",           "High pitched metal bell"),
    (68, "Low Agogo",            "Low pitched metal bell"),
]

SILENT_KEYWORDS = {'0', '-1', 'silent', 'silence', 'rest', 'none', 'mute', 'muted', 'off', 'unvoiced'}

# Friendly instrument aliases mapped to GM Percussion notes
GM_ALIASES = {
    'kick': 36, 'bassdrum': 36, 'bd': 36,
    'snare': 38, 'sd': 38, 'acousticsnare': 38,
    'rimshot': 37, 'sidestick': 37, 'rim': 37,
    'handclap': 39, 'clap': 39,
    'electricsnare': 40,
    'lowfloortom': 41, 'floortom': 41,
    'closedhihat': 42, 'hihat': 42, 'hh': 42, 'closedhh': 42,
    'highfloortom': 43,
    'pedalhihat': 44,
    'lowtom': 45,
    'openhihat': 46, 'openhh': 46,
    'lowmidtom': 47,
    'himidtom': 48,
    'crash': 49, 'crashcymbal': 49,
    'hightom': 50,
    'ride': 51, 'ridecymbal': 51,
    'chinesecymbal': 52,
    'ridebell': 53,
    'tambourine': 54,
    'splash': 55, 'splashcymbal': 55,
    'cowbell': 56,
    'crash2': 57,
    'vibraslap': 58,
    'ride2': 59,
    'highbongo': 60, 'bongo': 60,
    'lowbongo': 61,
    'muteconga': 62,
    'openconga': 63, 'conga': 63,
    'lowconga': 64,
    'hightimbale': 65, 'timbale': 65,
    'lowtimbale': 66,
    'highagogo': 67, 'agogo': 67,
    'lowagogo': 68,
    'cabasa': 69,
    'maracas': 70, 'maraca': 70,
    'shortwhistle': 71, 'whistle': 71,
    'longwhistle': 72,
    'shortguiro': 73, 'guiro': 73,
    'longguiro': 74,
    'claves': 75, 'clave': 75,
    'highwoodblock': 76, 'woodblock': 76,
    'lowwoodblock': 77,
    'mutecuica': 78, 'cuica': 78,
    'opencuica': 79,
    'mutetriangle': 80,
    'triangle': 81, 'opentriangle': 81,
}

def find_index_file() -> Optional[str]:
    """Find the path to hexdec/data/hexadecality_index.txt."""
    candidates = [
        # Relative to realpath of this script (handles symlinks)
        os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "hexdec", "data", "hexadecality_index.txt"),
        "hexdec/data/hexadecality_index.txt",
        "data/hexadecality_index.txt",
        os.path.expanduser("~/gemai/composit/hexdec/data/hexadecality_index.txt"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)
    return None

def parse_catalogue_specifier(spec: str) -> Optional[Tuple[str, int]]:
    """
    Check if a string matches catalogue specifiers:
      T01152.3, T1152.3, T01152, T1152
      D001.2, D1.2, D001, D1
      M01.1, M1, M01
    Returns (canonical_id, phase_index) or None.
    """
    cleaned = spec.strip()
    m = re.match(r'^([TMDtmd])(\d+)(?:\.(\d+))?$', cleaned)
    if not m:
        return None
    class_letter = m.group(1).upper()
    num = int(m.group(2))
    phase = int(m.group(3)) if m.group(3) else 1
    
    if class_letter == 'M':
        canonical_id = f"M{num:02d}"
    elif class_letter == 'D':
        canonical_id = f"D{num:03d}"
    elif class_letter == 'T':
        canonical_id = f"T{num:05d}"
    else:
        return None
    return canonical_id, phase

def lookup_catalogue_specifier(canonical_id: str, phase: int) -> Tuple[str, str, int, int]:
    """
    Look up a catalogue record from hexadecality_index.txt.
    Returns (partition_str, macro_type, phase, total_phases).
    """
    index_file = find_index_file()
    if not index_file:
        raise FileNotFoundError(
            "Could not locate 'hexadecality_index.txt'. Ensure 'hexdec/data/hexadecality_index.txt' exists."
        )
        
    with open(index_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith(canonical_id):
                # Extract all partitions in the orbital cycle
                parts = re.findall(r'(/(?:[0-9A-Fa-f]{4}/){4})', line)
                if not parts:
                    parts = re.findall(r'(/(?:[0-9A-Fa-f]+/)+)', line)
                if not parts:
                    raise ValueError(f"Could not extract partition from index entry: {line.strip()}")
                total_phases = len(parts)
                if phase < 1 or phase > total_phases:
                    raise IndexError(
                        f"Pattern index {phase} out of range for {canonical_id} (available phases: 1..{total_phases})"
                    )
                macro_type = "Monomer" if canonical_id.startswith("M") else (
                    "Dimer" if canonical_id.startswith("D") else "Tetramer"
                )
                return parts[phase - 1], macro_type, phase, total_phases
                
    raise KeyError(f"Catalogue identifier '{canonical_id}' not found in index.")

def encode_vlq(value: int) -> bytes:
    """Encode an integer as a MIDI Variable-Length Quantity (VLQ)."""
    bytes_arr = []
    bytes_arr.append(value & 0x7F)
    value >>= 7
    while value > 0:
        bytes_arr.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(bytes_arr))

def build_midi_track(events: list, total_ticks: int = 0) -> bytes:
    """Sort absolute-tick timed events and assemble into an SMF MTrk chunk."""
    # Note-offs (0x89) should precede note-ons (0x99) if they occur at the exact same tick
    events.sort(key=lambda ev: (ev[0], 0 if ev[1].startswith(b'\x89') else 1))
    
    track_data = bytearray()
    last_tick = 0
    
    for tick, ev_bytes in events:
        delta = tick - last_tick
        track_data.extend(encode_vlq(delta))
        track_data.extend(ev_bytes)
        last_tick = tick
        
    # Ensure track duration extends to total_ticks (crucial when trailing parts are silent)
    end_tick = max(last_tick, total_ticks)
    delta_end = end_tick - last_tick
    track_data.extend(encode_vlq(delta_end))
    track_data.extend(b'\xFF\x2F\x00')
    
    return b'MTrk' + struct.pack('>I', len(track_data)) + bytes(track_data)

def parse_partition_string(raw_str: str) -> List[List[int]]:
    """
    Parse a partition string in slash, comma, semicolon, or whitespace format.
    Supports:
      1. Base-36 characters (0-9: 0..9, A-Z / a-z: 10..35).
      2. Hyphenated, comma-separated, or space-separated multi-digit integers.
    """
    s = raw_str.strip()
    
    # Strip outer slashes if enclosed
    if s.startswith('/') and s.endswith('/') and len(s) > 1:
        s = s[1:-1]
        
    # Determine block delimiter
    if '/' in s:
        raw_blocks = [b.strip() for b in s.split('/') if b.strip()]
    elif ';' in s:
        raw_blocks = [b.strip() for b in s.split(';') if b.strip()]
    elif ',' in s:
        raw_blocks = [b.strip() for b in s.split(',') if b.strip()]
    else:
        raw_blocks = [b.strip() for b in s.split() if b.strip()]
        
    if not raw_blocks:
        raise ValueError(f"Could not parse any blocks from partition string: '{raw_str}'")
        
    blocks = []
    for b_str in raw_blocks:
        # Check if block contains separated integers (hyphen, space, comma)
        if '-' in b_str or ' ' in b_str or ',' in b_str:
            elements = [int(x) for x in re.split(r'[-,\s]+', b_str) if x]
        else:
            # Parse Base-36 characters (0-9: 0..9, A-Z/a-z: 10..35)
            elements = []
            for ch in b_str:
                if ch.isalnum():
                    elements.append(int(ch, 36))
                else:
                    raise ValueError(f"Unrecognised character '{ch}' in block '{b_str}'")
        blocks.append(sorted(elements))
        
    return blocks

def validate_partition(blocks: List[List[int]]) -> Tuple[int, int, bool, str]:
    """
    Validate that the blocks form a proper partition of {0, ..., n-1}.
    Returns (n, k, is_valid, message).
    """
    k = len(blocks)
    all_elements = []
    for b in blocks:
        all_elements.extend(b)
        
    n = len(all_elements)
    element_set = set(all_elements)
    
    if len(element_set) != n:
        seen = set()
        dups = set()
        for x in all_elements:
            if x in seen:
                dups.add(x)
            seen.add(x)
        return (n, k, False, f"Duplicate elements detected: {sorted(list(dups))}")
        
    expected_set = set(range(n))
    if element_set != expected_set:
        missing = expected_set - element_set
        extra = element_set - expected_set
        msg = []
        if missing:
            msg.append(f"Missing elements: {sorted(list(missing))}")
        if extra:
            msg.append(f"Elements outside range [0, {n-1}]: {sorted(list(extra))}")
        return (n, k, False, "; ".join(msg))
        
    return (n, k, True, f"Valid partition of Z_{n} into {k} blocks")

def format_element_base36(x: int) -> str:
    """Format a single integer as Base-36 (0-9, A-Z)."""
    if 0 <= x <= 9:
        return str(x)
    elif 10 <= x <= 35:
        return chr(ord('A') + x - 10)
    else:
        return f"({x})"

def format_block(blk: List[int], max_elem: int = 35) -> str:
    """Format a block of integers using Base-36 (or hyphens if max_elem > 35)."""
    if max_elem <= 35:
        return "".join(format_element_base36(x) for x in blk)
    else:
        return "-".join(str(x) for x in blk)

def compute_block_strides(blk: List[int], n: int) -> Tuple[int, ...]:
    """Compute circular difference strides between successive elements in Z_n."""
    sb = sorted(blk)
    if len(sb) <= 1:
        return (n,)
    strides = []
    for i in range(len(sb)):
        diff = (sb[(i + 1) % len(sb)] - sb[i]) % n
        strides.append(diff)
    return tuple(strides)

def parse_instrument_token(token: str) -> int:
    """Parse an instrument token into a MIDI note number (0 for silent/rest)."""
    cleaned = token.lower().strip().replace('_', '').replace('-', '')
    if cleaned in SILENT_KEYWORDS:
        return 0
    if cleaned in GM_ALIASES:
        return GM_ALIASES[cleaned]
    try:
        val = int(token)
        if val <= 0:
            return 0
        return val
    except ValueError:
        raise ValueError(f"Unrecognised instrument name or MIDI note: '{token}'")

def parse_silent_spec(silent_args: List[str], num_blocks: int) -> Set[int]:
    """
    Parse silent part specifications (1-indexed: 1..k or 0-indexed: 0..k-1).
    Accepts integers, comma-separated lists, or ranges like '1-3' or '1..3'.
    Returns 0-indexed block indices.
    """
    silent_indices = set()
    for arg in silent_args:
        tokens = re.split(r'[, ]+', str(arg).strip())
        for token in tokens:
            if not token:
                continue
            range_match = re.match(r'^(\d+)(?:\.\.|-)(\d+)$', token)
            if range_match:
                start_p = int(range_match.group(1))
                end_p = int(range_match.group(2))
                for p in range(start_p, end_p + 1):
                    idx = p - 1 if p > 0 else 0
                    if 0 <= idx < num_blocks:
                        silent_indices.add(idx)
            else:
                try:
                    p = int(token)
                    if 1 <= p <= num_blocks:
                        silent_indices.add(p - 1)
                    elif p == 0:
                        silent_indices.add(0)
                    else:
                        print(f"Warning: Silent part {p} out of range [1, {num_blocks}]", file=sys.stderr)
                except ValueError:
                    print(f"Warning: Could not parse silent part token '{token}'", file=sys.stderr)
    return silent_indices

def write_partition_midi(blocks: List[List[int]], output_path: str, bars: int = 4, bpm: int = 120,
                         instruments: List[int] = None, ticks_per_quarter: int = 480,
                         accent_downbeats: bool = True, sort_by_onset: bool = True,
                         time_sig: str = "auto", grouping: Optional[List[int]] = None,
                         accents: Optional[List[int]] = None):
    """
    Generate an SMF Type 0 MIDI file for a multi-voice composite rhythm partition.
    Muted/silent instruments (note <= 0) produce unvoiced rests.
    For any cyclic universe Z_n, bars are properly signatured as n/16 (or user-specified),
    preventing artificial common-time compression for odd/additive meters like 11/16.
    """
    all_elements = [x for b in blocks for x in b]
    n = len(all_elements)
    k = len(blocks)
    
    if sort_by_onset:
        sorted_blocks = sorted(blocks, key=lambda b: min(b))
    else:
        sorted_blocks = blocks
        
    if instruments is None:
        instruments = [GM_PERCUSSION_PALETTE[i % len(GM_PERCUSSION_PALETTE)][0] for i in range(k)]
    elif len(instruments) < k:
        avail = [p[0] for p in GM_PERCUSSION_PALETTE]
        for i in range(len(instruments), k):
            instruments.append(avail[i % len(avail)])
            
    step_ticks = ticks_per_quarter // 4   # 16th note (semiquaver) = 120 ticks
    note_duration = int(step_ticks * 0.75) # 90 ticks duration
    bar_ticks = n * step_ticks             # Total ticks per bar
    total_ticks = bars * bar_ticks         # Exact total duration
    
    events = []
    
    # Meta Event: Track Name
    track_name = os.path.splitext(os.path.basename(output_path))[0]
    name_bytes = track_name.encode('ascii', errors='replace')
    events.append((0, b'\xFF\x03' + encode_vlq(len(name_bytes)) + name_bytes))
    
    # Meta Event: Time Signature (FF 58 04 nn dd cc bb)
    # nn: numerator
    # dd: denominator as power of 2 (2 -> 4 quarter note, 4 -> 16 sixteenth note)
    # cc: MIDI clocks per metronome click (24 clocks = 1 quarter note; 6 clocks = 1 sixteenth note)
    # bb: 32nd notes per 24 MIDI clocks (always 8)
    if time_sig == "auto":
        if n == 16:
            numerator = 4
            denom_pow2 = 2 # 2^2 = 4 (4/4 common time)
            clocks_per_click = 24
        else:
            numerator = n
            denom_pow2 = 4 # 2^4 = 16 (n/16 time signature)
            clocks_per_click = 6  # 6 MIDI clocks = 1 semiquaver click
    else:
        ts_m = re.match(r"^(\d+)/(\d+)$", time_sig.strip())
        if not ts_m:
            raise ValueError(f"Malformed --time-sig value '{time_sig}'. Expected 'auto' or 'N/D' like '11/16'")
        numerator = int(ts_m.group(1))
        denom_val = int(ts_m.group(2))
        power = 0
        cur = denom_val
        while cur > 1 and cur % 2 == 0:
            cur //= 2
            power += 1
        if cur != 1:
            raise ValueError(f"Time signature denominator must be a power of 2 (e.g. 4, 8, 16), got {denom_val}")
        denom_pow2 = power
        clocks_per_click = max(1, int(24 * (4 / denom_val)))
        
    events.append((0, b'\xFF\x58\x04' + bytes([numerator, denom_pow2, clocks_per_click, 8])))
    
    # Accent set resolution
    accent_set = set()
    if accents is not None:
        accent_set = set(accents)
    elif grouping is not None:
        curr = 0
        for g in grouping:
            accent_set.add(curr)
            curr += g
    elif n == 16:
        # Standard quarter-note grid for Z_16 (common time)
        accent_set = {0, 4, 8, 12}
    else:
        # General n != 16 (e.g. 11): only the bar downbeat is accented by default,
        # avoiding false common-time (v % 4 == 0) subdivisions.
        accent_set = {0}
    
    # Meta Event: Set Tempo (BPM)
    mpqn = int(60_000_000 / bpm)
    tempo_bytes = struct.pack('>I', mpqn)[1:]
    events.append((0, b'\xFF\x51\x03' + tempo_bytes))
    
    status_note_on = 0x99  # Channel 10 Note On
    status_note_off = 0x89 # Channel 10 Note Off
    
    for bar in range(bars):
        bar_offset = bar * bar_ticks
        for blk_idx, blk in enumerate(sorted_blocks):
            inst_note = instruments[blk_idx]
            if inst_note <= 0:
                # Silent voice: do not emit any note events
                continue
            for v in blk:
                tick_on = bar_offset + v * step_ticks
                tick_off = tick_on + note_duration
                
                # Dynamic velocity: primary downbeat on v=0 (115), secondary pulses in accent_set (105), others (95)
                if accent_downbeats:
                    if v == 0:
                        velocity = 115
                    elif v in accent_set:
                        velocity = 105
                    else:
                        velocity = 95
                else:
                    velocity = 100
                    
                events.append((tick_on, bytes([status_note_on, inst_note, velocity])))
                events.append((tick_off, bytes([status_note_off, inst_note, 0])))
                
    trk_chunk = build_midi_track(events, total_ticks=total_ticks)
    mthd_chunk = b'MThd' + struct.pack('>IHHH', 6, 0, 1, ticks_per_quarter)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(mthd_chunk)
        f.write(trk_chunk)

def main():
    parser = argparse.ArgumentParser(
        prog="midipartner",
        description="Convert mosaic set partitions and catalogue macro-orbits into interlocking percussion MIDI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Primary Catalogue Specifiers (Hexadecagonal Affine Macro-Orbits):
  %(prog)s T01152.3 --bpm 63 --bars 8
  %(prog)s T01152 -o T01152.mid
  %(prog)s D001.2 --bpm 90
  %(prog)s M01 --bars 4

  # Subtractive Synthesis & Silent Instrument Nomination:
  %(prog)s T01152.3 --silent 1 -o T01152_no_kick.mid
  %(prog)s T01152.3 -i silent 38 42 75

  # Extended Functionality: Arbitrary Partitions & Metric Grids (Z_n, n <= 36):
  %(prog)s "/0149/26AE/37BF/58CD/" -o chiral_breakbeat.mid
  %(prog)s "/012/345/678/" --bpm 108 -o trimer_z9.mid
  %(prog)s "/012345/6789AB/CDEFGH/IJKLMN/OPQRST/UVWXYZ/" -o z36.mid
  %(prog)s --list-instruments
        """
    )
    parser.add_argument("partition", nargs="?", default=None,
                        help="Catalogue specifier ('T01152.3', 'D001.2', 'M01') or raw partition string ('/0149/26AE/37BF/58CD/')")
    parser.add_argument("-p", "--partition", dest="opt_partition", metavar="SPEC", default=None,
                        help="Catalogue specifier or raw partition string (flag equivalent to positional argument)")
    parser.add_argument("-o", "--output", default=None, help="Output .mid filepath (default: auto-named from specifier/partition)")
    parser.add_argument("-b", "--bars", type=int, default=4, help="Number of repeating bars (default: 4)")
    parser.add_argument("--bpm", type=int, default=120, help="Tempo in beats per minute (default: 120)")
    parser.add_argument("-i", "--instruments", nargs="+", default=None,
                        help="Custom GM percussion note numbers, names ('kick', 'snare'), or 'silent'/'0' per part")
    parser.add_argument("--silent", "--mute", dest="silent_parts", nargs="+", default=None,
                        help="Nominate one or more partition parts (1-indexed: 1..k or 0-indexed: 0..k-1) to be silent")
    parser.add_argument("--time-sig", default="auto",
                        help="Time signature embedded in MIDI file (default: 'auto' -> 4/4 for Z_16, n/16 for general Z_n)")
    parser.add_argument("--grouping", default=None,
                        help="Additive metric pulse grouping for odd/additive meters (e.g. '3,3,3,2' for 11/16)")
    parser.add_argument("--accents", default=None,
                        help="Explicit accented step positions as comma-separated integers (e.g. '0,3,6,9')")
    parser.add_argument("--no-accent", action="store_true", help="Disable dynamic downbeat accenting")
    parser.add_argument("--no-sort-blocks", action="store_true", help="Keep exact block ordering without sorting by onset")
    parser.add_argument("--list-instruments", action="store_true", help="List available curated GM percussion voices")
    
    args = parser.parse_args()
    
    if args.list_instruments:
        print("Curated General MIDI Channel 10 Percussion Palette:")
        print(f"{'MIDI #':<8} {'Instrument Name':<24} {'Acoustic Register/Role'}")
        print("-" * 55)
        for num, name, role in GM_PERCUSSION_PALETTE:
            print(f"{num:<8} {name:<24} {role}")
        print("\nNote: Specify 'silent', 'rest', 'none', or '0' for unvoiced parts.")
        return
        
    input_str = args.opt_partition or args.partition
    if not input_str:
        parser.print_help()
        sys.exit(1)
        
    # Check if input is a catalogue specifier (e.g. T01152.3, D001, M01)
    spec_info = parse_catalogue_specifier(input_str)
    catalogue_meta = None
    default_base_name = None
    
    if spec_info is not None:
        canonical_id, phase_idx = spec_info
        try:
            raw_partition, macro_type, phase, total_phases = lookup_catalogue_specifier(canonical_id, phase_idx)
            catalogue_meta = {
                'id': canonical_id,
                'macro_type': macro_type,
                'phase': phase,
                'total_phases': total_phases,
            }
            partition_str = raw_partition
            if total_phases > 1 and phase > 1:
                default_base_name = f"{canonical_id}_{phase}"
            else:
                default_base_name = f"{canonical_id}"
        except Exception as err:
            print(f"Error resolving catalogue specifier '{input_str}': {err}", file=sys.stderr)
            sys.exit(1)
    else:
        partition_str = input_str
        
    try:
        blocks = parse_partition_string(partition_str)
    except Exception as e:
        print(f"Error parsing partition: {e}", file=sys.stderr)
        sys.exit(1)
        
    n, k, is_valid, val_msg = validate_partition(blocks)
    if not is_valid:
        print(f"Error: Invalid partition: {val_msg}", file=sys.stderr)
        sys.exit(1)
        
    # Sort blocks so Block 0 contains vertex 0 unless --no-sort-blocks is given
    if not args.no_sort_blocks:
        blocks = sorted(blocks, key=lambda b: min(b))
        
    block_sizes = [len(b) for b in blocks]
    shape_str = "".join(f"z_{sz}" for sz in sorted(block_sizes))
    
    # Determine default output filename if not supplied
    if args.output is None:
        if default_base_name:
            args.output = f"{default_base_name}.mid"
        else:
            partition_tag = "_".join(format_block(b, max_elem=n - 1) for b in blocks)
            args.output = f"mosaic_{n}step_{k}v_{partition_tag}.mid"
        
    # Parse instrument assignments
    if args.instruments is not None:
        try:
            inst_notes = [parse_instrument_token(tok) for tok in args.instruments]
        except ValueError as err:
            print(f"Error in --instruments: {err}", file=sys.stderr)
            sys.exit(1)
    else:
        inst_notes = [GM_PERCUSSION_PALETTE[i % len(GM_PERCUSSION_PALETTE)][0] for i in range(k)]
        
    # Pad if fewer instruments specified than blocks
    if len(inst_notes) < k:
        avail = [p[0] for p in GM_PERCUSSION_PALETTE]
        for i in range(len(inst_notes), k):
            inst_notes.append(avail[i % len(avail)])
            
    # Apply --silent / --mute nominations
    if args.silent_parts:
        silent_indices = parse_silent_spec(args.silent_parts, k)
        for idx in silent_indices:
            inst_notes[idx] = 0
            
    palette_dict = {num: (name, role) for num, name, role in GM_PERCUSSION_PALETTE}
    
    # Parse grouping if provided
    grouping_list = None
    if args.grouping:
        try:
            grouping_list = [int(x.strip()) for x in args.grouping.split(',') if x.strip()]
            if sum(grouping_list) != n:
                print(f"Warning: --grouping sum ({sum(grouping_list)}) does not equal cycle length {n}", file=sys.stderr)
        except ValueError:
            print(f"Error parsing --grouping '{args.grouping}'. Expected comma-separated integers e.g. '3,3,3,2'", file=sys.stderr)
            sys.exit(1)

    # Parse accents if provided
    accents_list = None
    if args.accents:
        try:
            accents_list = [int(x.strip()) for x in args.accents.split(',') if x.strip()]
        except ValueError:
            print(f"Error parsing --accents '{args.accents}'. Expected comma-separated integers e.g. '0,3,6,9'", file=sys.stderr)
            sys.exit(1)

    ts_label = args.time_sig if args.time_sig != "auto" else ("4/4 (common time)" if n == 16 else f"{n}/16")

    print("=" * 64)
    print("  midipartner: Mosaic Partition to MIDI Percussion Synthesizer")
    print("=" * 64)
    if catalogue_meta:
        print(f"Catalogue Record:    {catalogue_meta['id']} ({catalogue_meta['macro_type']}, Phase {catalogue_meta['phase']} of {catalogue_meta['total_phases']})")
    print(f"Input Partition:     {partition_str}")
    print(f"Time Signature:      {ts_label} ({n} semiquavers per bar)")
    if grouping_list:
        print(f"Metric Grouping:     {'+'.join(str(x) for x in grouping_list)} (additive pulse)")
    print(f"Percussive Voices:   {k} interlocking parts")
    print(f"Shape Decomposition: {shape_str} (block sizes: {block_sizes})")
    print(f"Tempo & Duration:    {args.bpm} BPM | {args.bars} bars ({args.bars * n} total semiquavers)")
    print(f"Output File:         {args.output}")
    print("-" * 64)
    print("Part & Voice Assignments:")
    for idx, (blk, note) in enumerate(zip(blocks, inst_notes)):
        part_num = idx + 1
        blk_rep = format_block(blk, max_elem=n - 1)
        strides = compute_block_strides(blk, n)
        if note <= 0:
            print(f"  Part {part_num} (Voice {idx}) [SILENT / REST             ]: onsets={blk_rep:<12} strides={strides} (unvoiced)")
        else:
            name, role = palette_dict.get(note, (f"Custom MIDI #{note}", "Percussion"))
            print(f"  Part {part_num} (Voice {idx}) [MIDI {note:2d} - {name:<20}]: onsets={blk_rep:<12} strides={strides}")
    print("-" * 64)
    
    write_partition_midi(
        blocks=blocks,
        output_path=args.output,
        bars=args.bars,
        bpm=args.bpm,
        instruments=inst_notes,
        accent_downbeats=not args.no_accent,
        sort_by_onset=not args.no_sort_blocks,
        time_sig=args.time_sig,
        grouping=grouping_list,
        accents=accents_list
    )
    
    filesize = os.path.getsize(args.output)
    print(f"✓ Successfully generated SMF MIDI file: {args.output} ({filesize} bytes)")

if __name__ == "__main__":
    main()
