#!/usr/bin/env bash
# compile_atlas_parts.sh - Parallel compilation of 4 Tetramer Atlas plate chunks
# Total: 216 pages (54 pages x 4 chunks = 20,721 Tetramers)
# Author: Gemma Knee and Antigra Vitti

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEXDEC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLATES_DIR="$HEXDEC_DIR/plates"

echo "=== Starting Parallel Compilation of Tetramer Atlas Plates ==="
echo "Working directory: $HEXDEC_DIR"
echo "Target plates: tetramers_part1.tex .. tetramers_part4.tex"

t_start=$(date +%s)

# Compile 4 parts in parallel
(cd "$HEXDEC_DIR" && pdflatex -interaction=nonstopmode -output-directory=plates plates/tetramers_part1.tex > plates/tetramers_part1.build.log 2>&1) &
pid1=$!

(cd "$HEXDEC_DIR" && pdflatex -interaction=nonstopmode -output-directory=plates plates/tetramers_part2.tex > plates/tetramers_part2.build.log 2>&1) &
pid2=$!

(cd "$HEXDEC_DIR" && pdflatex -interaction=nonstopmode -output-directory=plates plates/tetramers_part3.tex > plates/tetramers_part3.build.log 2>&1) &
pid3=$!

(cd "$HEXDEC_DIR" && pdflatex -interaction=nonstopmode -output-directory=plates plates/tetramers_part4.tex > plates/tetramers_part4.build.log 2>&1) &
pid4=$!

echo "Dispatched 4 parallel pdflatex jobs (PIDs: $pid1, $pid2, $pid3, $pid4)..."

# Wait for each job and check status
wait $pid1
status1=$?
echo "Part 1 finished with status $status1"

wait $pid2
status2=$?
echo "Part 2 finished with status $status2"

wait $pid3
status3=$?
echo "Part 3 finished with status $status3"

wait $pid4
status4=$?
echo "Part 4 finished with status $status4"

if [ $status1 -ne 0 ] || [ $status2 -ne 0 ] || [ $status3 -ne 0 ] || [ $status4 -ne 0 ]; then
    echo "ERROR: One or more pdflatex compilation jobs failed!"
    exit 1
fi

t_compiled=$(date +%s)
echo "✓ All 4 parts compiled successfully in $((t_compiled - t_start)) seconds."

echo "=== Merging 4 Parts into Master Atlas (pdfunite) ==="
pdfunite "$PLATES_DIR/tetramers_part1.pdf" \
         "$PLATES_DIR/tetramers_part2.pdf" \
         "$PLATES_DIR/tetramers_part3.pdf" \
         "$PLATES_DIR/tetramers_part4.pdf" \
         "$PLATES_DIR/tetramers_atlas.pdf"

t_end=$(date +%s)
echo "✓ tetramers_atlas.pdf created successfully in $((t_end - t_compiled)) seconds."
echo "=== Atlas Build Complete: Total Time $((t_end - t_start)) seconds ==="

pdfinfo "$PLATES_DIR/tetramers_atlas.pdf" | grep -E "Pages:|File size:"
