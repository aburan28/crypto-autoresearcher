#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
dot -Tsvg mechanism.dot -o mechanism.svg
dot -Tpdf mechanism.dot -o mechanism.pdf
{
  cat PLAN.md
  printf '\n\\newpage\n\n## Mechanism and validation dependencies\n\n'
  printf '![Classical computation only. Known constructions are blue; the missing EC-specific operation is dashed amber. All downstream tests are pending. No measured speedup is depicted.](mechanism.pdf){width=82%%}\n\n'
  printf '\n\\newpage\n\n'
  cat SOURCES.md
} > report-source.md
pandoc report-source.md --standalone --from=markdown+tex_math_dollars \
  --pdf-engine=xelatex -V geometry:margin=20mm -V fontsize=10pt \
  -V mainfont='DejaVu Serif' -V sansfont='DejaVu Sans' \
  -V monofont='DejaVu Sans Mono' -V colorlinks=true -V urlcolor=blue \
  -o report.pdf
pandoc report-source.md --standalone --from=markdown+tex_math_dollars \
  -V geometry:margin=20mm -V fontsize=10pt \
  -V mainfont='DejaVu Serif' -V sansfont='DejaVu Sans' \
  -V monofont='DejaVu Sans Mono' -V colorlinks=true -V urlcolor=blue \
  -o report.tex
