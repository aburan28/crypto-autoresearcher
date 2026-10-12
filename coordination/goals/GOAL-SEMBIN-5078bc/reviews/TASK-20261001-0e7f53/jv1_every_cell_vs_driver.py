"""JV-1 attack step 1, completion: evaluate EVERY cell of the v2 sweep (all four
models, every budget, both d bounds) with the snapshot's own cost function
(code/v2/model_v2.py extracted from commit b8019a6fb, not the working tree) and
with the JV-1 header-block implementation, and diff field by field.

The JV-1 implementation (jv1_header_model.py) was written and frozen before
model_v2.py was read.
"""
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm  # noqa: E402

REPO = HERE.parents[4]
SNAP = "b8019a6fb"
SRC = "experiments/EXP-SEMBIN-04ec3c/code/v2/model_v2.py"

with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "model_v2_snapshot.py"
    p.write_bytes(subprocess.check_output(["git", "-C", str(REPO), "show", f"{SNAP}:{SRC}"]))
    spec = importlib.util.spec_from_file_location("model_v2_snapshot", p)
    mv2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mv2)

mv2.set_subgroup_order_log2(math.log2(hm.R_ECC2K130))
fields = ("s", "TPR", "CALLS", "PROBE", "FILL", "LA", "TOTAL")
maxd = {f: 0.0 for f in fields}
s_mism = 0
dom_mism = 0
fill_zero_literal = 0  # cells where v2 FILL=0.0 exponent (2^0 = 1 op) vs JV-1 FILL=0 exponent
cells = 0
for bound_label, bound_of in (("n", lambda n: float(n)), ("n/2", lambda n: n / 2.0)):
    def visit(n, model, b, m, d, cell):
        global cells, s_mism, dom_mism
        cells += 1
        mine = hm.cell(n, m, d, model, b)
        if cell[0] != mine["s"]:
            s_mism += 1
        for i, f in enumerate(fields[1:], start=1):
            maxd[f] = max(maxd[f], abs(cell[i] - mine[f]))
        if (cell[2] < 0) != mine["out_of_domain"]:
            dom_mism += 1
    mv2.sweep(mv2.DEGREES, range(2, 17), mv2.MODELS, visit, bound_of=bound_of)

out = dict(snapshot=SNAP, driver=SRC, cells_compared=cells, s_mismatches=s_mism,
           domain_flag_mismatches=dom_mism, max_abs_diff_bits=maxd)
(HERE / "jv1_every_cell_vs_driver_output.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
