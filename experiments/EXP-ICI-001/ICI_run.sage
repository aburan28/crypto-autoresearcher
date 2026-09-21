# ICI_run.sage — driver for EXP-ICI-001 (H-ICI-001, TASK-20260718-ICI).
# Usage: sage experiments/EXP-ICI-001/ICI_run.sage --path crossbred --run-id RUN-EXP-ICI-001-a \
#          --out experiments/EXP-ICI-001/runs/RUN-EXP-ICI-001-a/raw.json --ladder 10,12,14,16,18 [options]
# Thin wrapper: all machinery lives in ici_lib.py (plain Python, not preparsed).

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ici_lib

if __name__ == "__main__":
    ici_lib.main()
