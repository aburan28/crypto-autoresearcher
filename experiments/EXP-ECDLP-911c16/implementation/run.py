#!/usr/bin/env python3
"""Direct native selected-route driver; no standalone trial authority."""
from pathlib import Path
import importlib.util
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
path = ROOT / "coordination/tasks/TASK-20261018-993753/worksheet_envelope.py"
spec = importlib.util.spec_from_file_location("worksheet_metadata", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if __name__ == "__main__":
    module.run()

