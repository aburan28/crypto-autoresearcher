"""Conditional S launcher; requires its own native frozen admission and W gate."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'research/prym_experiment_design_20261019/implementation'))
from native_runtime_v2 import main
from selector_pipeline import run
if __name__=='__main__':raise SystemExit(main('EXP-ECDLP-5e7e74',run))
