"""J12 (ii) trend (TASK-20260926-c58e87): saturation margin of the convolution forms on the
diagonal l = (n+1)/2 (x_1 x_2 never reduces: 2l - 1 = n), modulus-free. Counting only.
margin0 = (rows_M4 - P) - trivial - dim B_{<=3}; margin_ell = margin0 - (nv - 1) (ell-syzygy
count measured 17 = nv - 1 at n = 17; nv - 1 assumed elsewhere). Usage: python3 n_trend.py <out.json>"""
import json, sys, time
from math import comb
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from n19_counting import P_rank, conv_forms
res = []
for n in (13, 15, 17, 19, 21, 23):
    l = (n + 1) // 2; nv = 2 * l
    t = time.time(); P = P_rank(conv_forms(n, l), nv)
    rows = n * (1 + nv + comb(nv, 2)); b3 = sum(comb(nv, i) for i in range(4)); triv = comb(n, 2) + n
    m0 = rows - P - triv - b3
    r = {"n": n, "l": l, "nv": nv, "rows_M4": rows, "P_conv": P, "dim_Z_top": rows - P, "trivial": triv,
         "dim_B_le3": b3, "margin_no_ell": m0, "margin_with_ell_syz": m0 - (nv - 1), "seconds": round(time.time() - t, 1)}
    res.append(r); print(json.dumps(r), flush=True)
json.dump(res, open(sys.argv[1], "w"), indent=1)
