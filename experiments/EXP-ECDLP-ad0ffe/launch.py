"""Native admitted W launcher; scientific stream lives in bound implementation."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'research/prym_experiment_design_20261019/implementation'))
from native_runtime import main
from witness import run
if __name__=='__main__':raise SystemExit(main('EXP-ECDLP-ad0ffe',run))
