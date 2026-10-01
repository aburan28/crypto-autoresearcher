"""O4 pre-engine quantities (TASK-20260926-c58e87). Own code only; NO ENGINE CALL.
For every O4 slot: P' = rank of the degree-4 projection of M_4 of E'_S3(x_R)'s quadratic part
(L-TOP: shared by the V' descent and both kept N-CONV-VR systems at that slot), the saturation
arithmetic, the left-kernel dimension of the quadratic-column submatrix (rc_b step 1) for every
O4 system, and ell's linear support. Also the multiplication-tensor statistic that separates V'
from the polynomial basis: the number of distinct products b_i b_j (i, j < 9).
Usage: python3 o4_prepredict.py <j10-ptm dir>
"""
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rtlib as R  # noqa: E402

d = sys.argv[1]
S = json.load(open(f"{d}/o4-systems.json"))
BS = json.load(open(f"{d}/o4-basis-and-support.json"))
basis = BS["support"]["basis"]
out = {"basis": basis, "per_slot": [], "per_system": []}
prods = {R.gmul(basis[i], basis[j]) for i in range(9) for j in range(9)}
pb = R.poly_basis()
out["distinct_products_bi_bj"] = {"V_prime": len(prods),
                                  "polynomial_basis": len({R.gmul(pb[i], pb[j]) for i in range(9) for j in range(9)})}
# span dimension of the products
ech = R.Echelon()
for x in prods:
    ech.add(x)
out["span_dim_products_V_prime"] = ech.dim()
for dd in S["descents"]:
    E = R.hex_to_E(dd["E_hex"])
    P = R.P_rank(E)
    kd, c = R.left_kernel_dim_quadratic(E)
    ellinfo = None
    if kd == 1:
        lin = [0] * 19
        for k in range(17):
            if (c >> k) & 1:
                for col in range(19):
                    lin[col] ^= int(E[k, col])
        ellinfo = {"linear_support": [j for j in range(18) if lin[1 + j]], "const": lin[0],
                   "c_eq_Tr_tk_over_xR2": all(((c >> k) & 1) == R.gtr(R.gmul(1 << k, R.ginv(R.gsq(dd["x_R"])))) for k in range(17))}
    Z = 2924 - P
    out["per_slot"].append({"slot": dd["slot"], "idx": dd["idx"], "x_R": dd["x_R"], "P_prime": P,
                            "dim_Z_top": Z, "Z_minus_153": Z - 153, "excess_over_988": Z - 153 - 988,
                            "descent_s": dd["s"], "descent_kernel_dim": kd, "descent_ell": ellinfo})
for k in S["kept"]:
    if "EXHAUSTED" in k:
        continue
    E = R.hex_to_E(k["E_hex"])
    kd, c = R.left_kernel_dim_quadratic(E)
    lin = None
    if kd == 1:
        l = [0] * 19
        for kk in range(17):
            if (c >> kk) & 1:
                for col in range(19):
                    l[col] ^= int(E[kk, col])
        lin = {"linear_support_size": sum(l[1:]), "const": l[0]}
    out["per_system"].append({"key": k["key"], "s": k["s"], "attempt": k["attempt"], "kernel_dim": kd,
                              "ell": lin, "P_check": R.P_rank(E)})
print(json.dumps({k: v for k, v in out.items() if k not in ("per_system",)}, indent=0)[:6000])
print("per_system P set:", sorted({r["P_check"] for r in out["per_system"]}),
      "kernel dims:", sorted({r["kernel_dim"] for r in out["per_system"]}))
json.dump(out, open(f"{d}/o4-prepredict.json", "w"), indent=1)
