"""JV-1: localise the C-3 min-slack difference (raw vs JV-1 in-domain-only).
Recompute min over ALL primary cells (in and out of domain), bound-n grid."""
import json, math, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm
from jv1_diff_primary import COMBOS, PRIMARY, MS, grid, log2B, load_raw
raw = load_raw()
rs = raw["generic_lower_bound_flag"]["min_slack_bits_by_degree"]
out = {}
for n in hm.DEGREES:
    N = hm.N_of(n)
    mn_all, mn_in, arg_all = math.inf, math.inf, None
    for model, b in COMBOS:
        if model not in PRIMARY: continue
        for m in MS:
            for d in grid(float(n)):
                c = hm.cell(n, m, d, model, log2B(b))
                sl = c["TOTAL"] - (N/2 - 2.0)
                if sl < mn_all: mn_all, arg_all = sl, (model, b, m, d, c["CALLS"])
                if not c["out_of_domain"]: mn_in = min(mn_in, sl)
    out[n] = dict(raw=rs[str(n)], all_cells=mn_all, in_domain=mn_in, diff_all_vs_raw=mn_all-rs[str(n)], argmin_all=arg_all)
    print(n, out[n])
(HERE/"jv1_flag_slack_check_output.json").write_text(json.dumps(out, indent=1, default=str))
