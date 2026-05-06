#!/bin/bash
# Regenerate all figures referenced in the paper from the released runs/ tree.
# Output PDFs are written next to each script.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo "[1/3] Leaderboard performance (Fig. 1)"
python generate_plot.py

echo "[2/3] Efficiency Pareto frontier (Fig. 2)"
python analyses/a5_efficiency_pareto.py

echo "[3/3] Public-private gap (Fig. 4)"
python analyses/a3_public_private_gap.py

echo
echo "Done. Figures written to $HERE/"
