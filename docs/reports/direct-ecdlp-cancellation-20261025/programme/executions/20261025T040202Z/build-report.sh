#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 plot.py
pandoc REPORT.md --standalone --from=markdown+tex_math_dollars --pdf-engine=xelatex \
  -V geometry:margin=20mm -V fontsize=10pt -V mainfont='DejaVu Serif' \
  -V sansfont='DejaVu Sans' -V monofont='DejaVu Sans Mono' \
  -V colorlinks=true -V urlcolor=blue -o report.pdf
