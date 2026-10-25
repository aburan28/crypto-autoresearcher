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

# Complete the documented format-only export; no scientific experiment runs.
compact_repo_root=$(git rev-parse --show-toplevel)
compact_output_dir=$(mktemp -d)
trap 'rm -rf -- "$compact_output_dir"' EXIT
python3 "$compact_repo_root/docs/reports/direct-ecdlp-cancellation-20261025/compact-export.py" \
  --repo-root "$compact_repo_root" --out-dir "$compact_output_dir"
cp -- "$compact_output_dir/docs/reports/direct-ecdlp-cancellation-20261025/programme/report.pdf" report.pdf
