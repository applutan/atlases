#!/usr/bin/env bash
# render_atlas_samples.sh - Render sample PNG plates from the Tetramer Atlas and Master Book
# Author: Gemma Knee and Antigra Vitti

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEXDEC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLATES_DIR="$HEXDEC_DIR/plates"
REPORTS_DIR="$HEXDEC_DIR/reports"

mkdir -p "$REPORTS_DIR"

echo "=== Rendering High-Resolution Atlas Preview Plates ==="

# 1. First page of Atlas: Pure Cobalt Blue (s=4, highest symmetry)
pdftoppm -png -r 150 -f 1 -l 1 "$PLATES_DIR/tetramers_atlas.pdf" "$REPORTS_DIR/atlas_page_001"
mv "$REPORTS_DIR/atlas_page_001-1.png" "$REPORTS_DIR/atlas_page_001.png" 2>/dev/null || true
echo "✓ Rendered Atlas Page 1 (s=4 Cobalt Blue): $REPORTS_DIR/atlas_page_001.png"

# 2. Mid page of Atlas: Page 108 (Tetramers 10273..10368)
pdftoppm -png -r 150 -f 108 -l 108 "$PLATES_DIR/tetramers_atlas.pdf" "$REPORTS_DIR/atlas_page_108"
mv "$REPORTS_DIR/atlas_page_108-108.png" "$REPORTS_DIR/atlas_page_108.png" 2>/dev/null || true
echo "✓ Rendered Atlas Page 108 (Mid Atlas): $REPORTS_DIR/atlas_page_108.png"

# 3. Final page of Atlas: Page 216 (Finale, Chiral Pink)
pdftoppm -png -r 150 -f 216 -l 216 "$PLATES_DIR/tetramers_atlas.pdf" "$REPORTS_DIR/atlas_page_216"
mv "$REPORTS_DIR/atlas_page_216-216.png" "$REPORTS_DIR/atlas_page_216.png" 2>/dev/null || true
echo "✓ Rendered Atlas Page 216 (Chiral Finale): $REPORTS_DIR/atlas_page_216.png"

echo "=== Atlas Sample Previews Rendered Successfully ==="
