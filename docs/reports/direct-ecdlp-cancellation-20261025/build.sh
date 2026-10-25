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

# Complete the documented format-only export; no scientific experiment runs.
compact_repo_root=$(git rev-parse --show-toplevel)
compact_output_dir=$(mktemp -d)
trap 'rm -rf -- "$compact_output_dir"' EXIT
python3 "$compact_repo_root/docs/reports/direct-ecdlp-cancellation-20261025/compact-export.py" \
  --repo-root "$compact_repo_root" --out-dir "$compact_output_dir"
cp -- "$compact_output_dir/docs/reports/direct-ecdlp-cancellation-20261025/report.pdf" report.pdf
