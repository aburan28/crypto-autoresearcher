#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 plot.py
{
  cat HEADER.md
  printf '\n\\newpage\n\n'
  cat observations.md
  printf '\n\\newpage\n\n'
  printf '## Recorded execution and circuit sizes\n\n'
  printf '![RUN-ECDLP-d7f049: actual module start/end intervals. Builds and self-tests ran sequentially first. Different workloads and concurrent host load preclude interpreting these durations as algorithm comparisons.](execution.pdf){width=95%%}\n\n'
  printf '![RUN-ECDLP-d7f049: gate-node counts recorded for all eight forward circuits. Blue: main curves; amber: separate j=0 controls. No extrapolation or inversion complexity is inferred.](circuits.pdf){width=95%%}\n'
  printf '\n\\newpage\n\n'
  printf '## Exact entropy observations and controls\n\n'
  printf '![RUN-ECDLP-d7f049: eight Kummer rows. Observed full-pair entropy is exact apart from numerical logarithms; bars show the spread of the 99 unconditional null draws, not uncertainty on an attack gain. Matched means coincide with observations to roundoff.](kummer-controls.pdf){width=95%%}\n\n'
  printf '![RUN-ECDLP-d7f049: all 22 projection families on eight fixtures. Primary reference is sign-pair matched for negation-invariant projections and unconditional otherwise. Gray cells are inapplicable power residues. Differences are descriptive, without significance, multiplicity correction, or scalar-recovery interpretation.](projection-panel.pdf){width=86%%}\n'
} > report-source.md
pandoc report-source.md --standalone --from=markdown+tex_math_dollars --pdf-engine=xelatex \
  -V geometry:margin=18mm -V fontsize=10pt -V mainfont='DejaVu Serif' \
  -V sansfont='DejaVu Sans' -V monofont='DejaVu Sans Mono' \
  -V colorlinks=true -V urlcolor=blue -o report.pdf

# Complete the documented format-only export; no scientific experiment runs.
compact_repo_root=$(git rev-parse --show-toplevel)
compact_output_dir=$(mktemp -d)
trap 'rm -rf -- "$compact_output_dir"' EXIT
python3 "$compact_repo_root/docs/reports/direct-ecdlp-cancellation-20261025/compact-export.py" \
  --repo-root "$compact_repo_root" --out-dir "$compact_output_dir"
cp -- "$compact_output_dir/experiments/EXP-ECDLP-fe3337/reports/run-20261025T0526Z/report.pdf" report.pdf
