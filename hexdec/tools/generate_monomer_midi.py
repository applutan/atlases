#!/usr/bin/env python3
"""
generate_monomer_midi.py - Generate MIDI Percussion Files for the 14 Monomers of z_4^4 on Z_16

Creates 14 Standard MIDI Files (SMF Format 0):
  monomer1.mid, monomer2.mid, ..., monomer9.mid, monomera.mid, ..., monomere.mid

Each file uses four distinct General MIDI non-melodic percussive instruments on Channel 10:
  - Block 0 (containing vertex 0, downbeat): Bass Drum 1 (Kick, note 36)
  - Block 1: Acoustic Snare (note 38)
  - Block 2: Closed Hi-Hat (note 42)
  - Block 3: Claves (note 75)

The 16 vertices of Z_16 map to the 16 sixteenth-note steps of a 4/4 measure.
Because each mosaic is a strict set partition, exactly one instrument strikes at each step,
forming an interlocking, non-overlapping 16-step composite polyrhythm (hocket).

Author: Gemma Knee
"""

import sys
import os
import struct
import argparse
from collections import defaultdict

# Add workspace root for access to tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.affine_macro_orbits import find_fixed_point_orbits

def encode_vlq(value: int) -> bytes:
    """Encode an integer as a MIDI Variable-Length Quantity (VLQ)."""
    bytes_arr = []
    bytes_arr.append(value & 0x7F)
    value >>= 7
    while value > 0:
        bytes_arr.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(bytes_arr))

def build_midi_track(events: list) -> bytes:
    """
    Given a list of absolute-tick timed events: (tick, event_bytes),
    sort them by tick and assemble into an SMF MTrk chunk with delta times.
    """
    events.sort(key=lambda ev: (ev[0], 0 if ev[1].startswith(b'\x89') else 1))
    
    track_data = bytearray()
    last_tick = 0
    
    for tick, ev_bytes in events:
        delta = tick - last_tick
        track_data.extend(encode_vlq(delta))
        track_data.extend(ev_bytes)
        last_tick = tick
        
    # End of Track meta event: delta 0, FF 2F 00
    track_data.extend(encode_vlq(0))
    track_data.extend(b'\xFF\x2F\x00')
    
    # MTrk chunk: 4-byte magic + 4-byte length + track data
    trk_chunk = b'MTrk' + struct.pack('>I', len(track_data)) + bytes(track_data)
    return trk_chunk

def create_monomer_midi(blocks: list, output_path: str, bars: int = 4, bpm: int = 120,
                        instruments: list = None, ticks_per_quarter: int = 480):
    """
    Generate an SMF Type 0 MIDI file for a single monomer mosaic.
    
    Parameters:
      blocks: list of 4 blocks, each containing 4 vertex indices in 0..15.
      output_path: path to write .mid file.
      bars: number of 4/4 bars to repeat.
      bpm: tempo in beats per minute.
      instruments: 4 MIDI note numbers on Channel 10.
    """
    if instruments is None:
        # Standard GM percussion notes:
        # 36 = Bass Drum 1, 38 = Acoustic Snare, 42 = Closed Hi-Hat, 75 = Claves
        instruments = [36, 38, 42, 75]
        
    step_ticks = ticks_per_quarter // 4  # 16th note = 120 ticks
    note_duration = int(step_ticks * 0.75) # 90 ticks duration
    bar_ticks = ticks_per_quarter * 4     # 1920 ticks per bar
    
    # Sort blocks so Block 0 contains vertex 0 (downbeat)
    sorted_blocks = sorted(blocks, key=lambda blk: min(blk))
    
    events = []
    
    # Meta Event: Track Name
    monomer_name = os.path.splitext(os.path.basename(output_path))[0]
    name_bytes = monomer_name.encode('ascii')
    events.append((0, b'\xFF\x03' + encode_vlq(len(name_bytes)) + name_bytes))
    
    # Meta Event: Time Signature 4/4 (numerator 4, denominator 2^2, clocks/click 24, 32nd-notes/24-clocks 8)
    events.append((0, b'\xFF\x58\x04\x04\x02\x18\x08'))
    
    # Meta Event: Set Tempo (microseconds per quarter note = 60,000,000 / BPM)
    mpqn = int(60_000_000 / bpm)
    tempo_bytes = struct.pack('>I', mpqn)[1:] # 3 bytes
    events.append((0, b'\xFF\x51\x03' + tempo_bytes))
    
    # Generate notes for repeating bars
    # GM Percussion is on Channel 10 (0x9 in 0-based MIDI status nibble)
    status_note_on = 0x99  # Channel 10 Note On
    status_note_off = 0x89 # Channel 10 Note Off
    
    for bar in range(bars):
        bar_offset = bar * bar_ticks
        for blk_idx, blk in enumerate(sorted_blocks):
            inst_note = instruments[blk_idx]
            for v in blk:
                tick_on = bar_offset + v * step_ticks
                tick_off = tick_on + note_duration
                velocity = 100
                
                # Note On
                ev_on = bytes([status_note_on, inst_note, velocity])
                events.append((tick_on, ev_on))
                
                # Note Off
                ev_off = bytes([status_note_off, inst_note, 0])
                events.append((tick_off, ev_off))
                
    trk_chunk = build_midi_track(events)
    
    # Header Chunk: MThd, length 6, format 0, 1 track, ticks_per_quarter
    mthd_chunk = b'MThd' + struct.pack('>IHHH', 6, 0, 1, ticks_per_quarter)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(mthd_chunk)
        f.write(trk_chunk)

def main():
    parser = argparse.ArgumentParser(description="Generate MIDI files for the 14 Monomers of z_4^4.")
    parser.add_argument("--outdir", default="hexdec/midi", help="Output directory for MIDI files (default: hexdec/midi)")
    parser.add_argument("--bars", type=int, default=4, help="Number of bars to play (default: 4)")
    parser.add_argument("--bpm", type=int, default=120, help="Tempo in BPM (default: 120)")
    parser.add_argument("--instruments", type=int, nargs=4, default=[36, 38, 42, 75],
                        help="4 GM percussion note numbers on Ch.10 (default: 36 [Kick], 38 [Snare], 42 [Closed Hat], 75 [Claves])")
    args = parser.parse_args()
    
    # Retrieve the 14 monomers
    fixed_orbits = find_fixed_point_orbits(16, 4, 4)
    # Sort orbits by size, then canonical representative
    sorted_orbits = sorted(fixed_orbits, key=lambda o: (len(o), sorted([sorted(list(b)) for b in list(o)[0]])))
    
    inst_names = {
        36: "Bass Drum 1 (Kick)",
        38: "Acoustic Snare",
        42: "Closed Hi-Hat",
        75: "Claves",
        37: "Side Stick",
        56: "Cowbell"
    }
    
    print(f"=== Generating MIDI for {len(sorted_orbits)} Monomers ===")
    print(f"Output directory: {args.outdir}")
    print(f"Configuration: {args.bars} bars @ {args.bpm} BPM, Channel 10 General MIDI")
    print(f"Voices:")
    for i, inst in enumerate(args.instruments):
        desc = inst_names.get(inst, f"GM Perc #{inst}")
        print(f"  Voice {i} (Block {i}): MIDI {inst} [{desc}]")
    print("-" * 50)
    
    generated_files = []
    
    for idx, orb in enumerate(sorted_orbits, 1):
        rep = sorted(list(orb), key=lambda p: sorted([sorted(list(b)) for b in p]))[0]
        blocks = [sorted(list(b)) for b in rep]
        orb_sz = len(orb)
        
        # Hexadecimal label: 1..e
        hex_label = f"{idx:x}"
        filename = f"monomer{hex_label}.mid"
        filepath = os.path.join(args.outdir, filename)
        
        create_monomer_midi(
            blocks=blocks,
            output_path=filepath,
            bars=args.bars,
            bpm=args.bpm,
            instruments=args.instruments
        )
        
        filesize = os.path.getsize(filepath)
        generated_files.append((filename, orb_sz, blocks, filesize))
        print(f"[{idx:2d}/14] Generated {filename:<14} (D_16 size {orb_sz:2d}, {filesize} bytes)")
        
    print("-" * 50)
    print(f"✓ Successfully generated all 14 MIDI files in {args.outdir}")

if __name__ == "__main__":
    main()
