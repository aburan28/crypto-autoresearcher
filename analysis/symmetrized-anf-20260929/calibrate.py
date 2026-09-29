"""Measured distinct monomials of the descended symmetrized system against the
two upper bounds used in table.py.  Written to calibration.json."""
import json, glob
from math import log2
from table import dense, block, SUPPORT
rows = []
for f in ["descent_smoke.json", "descent_both.json", "descent_sym_large.json"]:
    for r in json.load(open(f)):
        n, m, l, d = r["n"], r["m"], r["l"], r["d_k"]
        W = [tuple(w) for w in SUPPORT[m]["maximal_weight_vectors"]]
        D = max(sum(min(w[k], d[k]) for k in range(m)) for w in W)
        meas = r["sym_main"]["distinct_monomials"]
        dn, bk = dense(sum(d), D), block(d, W)
        row = dict(n=n, m=m, l=l, measured_degree=r["sym_main"]["boolean_degree"],
                   predicted_degree=D, measured=meas, dense_bound=dn, block_bound=bk,
                   density_vs_dense=round(meas / dn, 4), density_vs_block=round(meas / bk, 4),
                   unsym_measured=(r["unsym"] or {}).get("distinct_monomials"),
                   log2_sym_minus_unsym=(round(log2((meas + r["sym_linking"]["distinct_monomials"]) / r["unsym"]["distinct_monomials"]), 2) if r["unsym"] else None))
        rows.append(row); print(row)
json.dump(rows, open("calibration.json", "w"), indent=1)
