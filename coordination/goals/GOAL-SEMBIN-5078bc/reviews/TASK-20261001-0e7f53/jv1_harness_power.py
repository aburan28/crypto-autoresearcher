"""JV-1 negative control on this review's own diff harness: run the same
every-cell comparison (jv1_every_cell_vs_driver.py logic) against the snapshot's
four mutant cost functions. A harness that reports 0.0 on the true driver must
report non-zero differences on each mutant, or its 0.0 is vacuous.
Degrees 97 and 131, bound n, all models and budgets.
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
MUT = "experiments/EXP-SEMBIN-04ec3c/code/v2/mutants/"
NAMES = ["M1_drop_L_from_TPR", "M2_tabulate_floor_m_minus_1_half",
         "M3_swap_time_and_store_halves", "M4_ceil_budget_cap"]
fields = ("s", "TPR", "CALLS", "PROBE", "FILL", "LA", "TOTAL")
res = {}
with tempfile.TemporaryDirectory() as td:
    for name in NAMES:
        p = Path(td) / f"{name}.py"
        p.write_bytes(subprocess.check_output(["git", "-C", str(REPO), "show", f"{SNAP}:{MUT}{name}.py"]))
        spec = importlib.util.spec_from_file_location(name, p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.set_subgroup_order_log2(math.log2(hm.R_ECC2K130))
        st = dict(cells=0, cells_differing=0, max_abs_TOTAL_diff=0.0, s_mismatches=0)

        def visit(n, model, b, m, d, cell):
            st["cells"] += 1
            mine = hm.cell(n, m, d, model, b)
            diff = any(abs(cell[i] - mine[f]) > 1e-9 for i, f in enumerate(fields) if i > 0) or cell[0] != mine["s"]
            st["cells_differing"] += diff
            st["s_mismatches"] += cell[0] != mine["s"]
            st["max_abs_TOTAL_diff"] = max(st["max_abs_TOTAL_diff"], abs(cell[6] - mine["TOTAL"]))
        mod.sweep((97, 131), range(2, 17), mod.MODELS, visit)
        res[name] = st
        print(name, st)
(HERE / "jv1_harness_power_output.json").write_text(json.dumps(res, indent=1))
