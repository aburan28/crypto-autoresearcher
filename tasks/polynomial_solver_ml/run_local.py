#!/usr/bin/env python3
"""Run the task without installing the parent research repository."""
import os
from pathlib import Path
import sys

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
sys.path.insert(0, str(Path(__file__).parent / "environment"))
from polynomial_ml.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
