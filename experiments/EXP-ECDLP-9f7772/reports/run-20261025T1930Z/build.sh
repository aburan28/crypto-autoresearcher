#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 make_report_text.py
python3 plot.py
