#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 render_map.py
non_generic_report_tmp=$(mktemp -d /tmp/non-generic-report.XXXXXX)
pandoc -f markdown+tex_math_single_backslash report.md --pdf-engine=pdflatex -V fontsize=10pt -V geometry:margin=0.65in -V fontfamily=mathptmx -V colorlinks=true -o "$non_generic_report_tmp/report-unpacked.pdf"
gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dPDFSETTINGS=/prepress -dSubsetFonts=true -dCompressFonts=true -dDetectDuplicateImages=true -sOutputFile=report.pdf "$non_generic_report_tmp/report-unpacked.pdf"
