#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
dot -Tsvg programme.dot -o programme.svg
dot -Tpdf programme.dot -o programme.pdf
{
  cat EXPERIMENTS.md
  printf '\n\\newpage\n\n'
  printf '![Completed development scaffolding and proposed scientific stages. Dashed amber boxes are pending; no measured speedup is depicted.](programme.pdf){width=78%%}\n'
  printf '\n\\newpage\n\n'
  cat LEADS.md
  printf '\n\\newpage\n\n'
  cat CHECKS.md
} > report-source.md
pandoc report-source.md --standalone --from=markdown+tex_math_dollars \
  --pdf-engine=xelatex -V geometry:margin=18mm -V fontsize=10pt \
  -V mainfont='DejaVu Serif' -V sansfont='DejaVu Sans' \
  -V monofont='DejaVu Sans Mono' -V colorlinks=true -V urlcolor=blue -o report.pdf
pandoc report-source.md --standalone --from=markdown+tex_math_dollars \
  -V geometry:margin=18mm -V fontsize=10pt \
  -V mainfont='DejaVu Serif' -V sansfont='DejaVu Sans' \
  -V monofont='DejaVu Sans Mono' -V colorlinks=true -V urlcolor=blue -o report.tex
