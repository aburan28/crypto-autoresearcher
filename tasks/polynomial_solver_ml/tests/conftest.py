from pathlib import Path
import os
import sys

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"

# Local layout and Harbor's /tests upload both import the same package.
local = Path(__file__).resolve().parents[1] / "environment"
sys.path.insert(0, str(local if local.is_dir() else Path("/app")))
